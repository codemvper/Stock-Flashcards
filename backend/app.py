# -*- coding: utf-8 -*-
"""
A股上市公司闪卡 - 后端API服务
使用Flask框架提供RESTful API
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import tushare as ts
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Tushare配置
TUSHARE_TOKEN = ''
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

# 缓存配置
CACHE_DIR = 'cache'
CACHE_TTL = 24  # 小时
HISTORICAL_CACHE_TTL = 7 * 24  # 历史数据缓存7天
STOCK_LIST_FILE = os.path.join(CACHE_DIR, 'stock_list.json')
STOCK_DATA_DIR = os.path.join(CACHE_DIR, 'stocks')
HISTORICAL_DATA_DIR = os.path.join(CACHE_DIR, 'historical')

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(STOCK_DATA_DIR, exist_ok=True)
os.makedirs(HISTORICAL_DATA_DIR, exist_ok=True)


def get_stock_list():
    """获取所有A股股票列表"""
    if os.path.exists(STOCK_LIST_FILE):
        with open(STOCK_LIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 检查缓存是否过期
            cache_time = datetime.fromisoformat(data['cache_time'])
            if datetime.now() - cache_time < timedelta(hours=CACHE_TTL):
                return data['stocks']
    
    try:
        # 从Tushare获取股票列表
        logger.info("从Tushare获取股票列表...")
        df = pro.stock_basic(exchange='', list_status='L', 
                            fields='ts_code,symbol,name,area,industry,market')
        stocks = df.to_dict('records')
        
        # 保存到缓存
        cache_data = {
            'cache_time': datetime.now().isoformat(),
            'stocks': stocks
        }
        with open(STOCK_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功获取 {len(stocks)} 只股票")
        return stocks
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return []


def get_stock_cache_path(ts_code):
    """获取股票缓存文件路径"""
    return os.path.join(STOCK_DATA_DIR, f'{ts_code}.json')


def is_cache_valid(cache_path):
    """检查缓存是否有效（24小时内）"""
    if not os.path.exists(cache_path):
        return False
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 检查是否有缓存时间字段
        if 'cached_time' not in data:
            logger.warning(f"缓存文件缺少时间戳: {cache_path}")
            return False
            
        # 解析缓存时间
        cache_time = datetime.fromisoformat(data['cached_time'])
        current_time = datetime.now()
        time_diff = current_time - cache_time
        
        # 检查是否在24小时内
        is_valid = time_diff < timedelta(hours=CACHE_TTL)
        
        if is_valid:
            logger.debug(f"缓存有效: {cache_path}, 缓存时间: {cache_time}, 剩余: {timedelta(hours=CACHE_TTL) - time_diff}")
        else:
            logger.debug(f"缓存过期: {cache_path}, 缓存时间: {cache_time}, 过期: {time_diff - timedelta(hours=CACHE_TTL)}")
            
        return is_valid
        
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f"缓存文件格式错误: {cache_path}, 错误: {e}")
        return False
    except Exception as e:
        logger.error(f"读取缓存文件失败: {cache_path}, 错误: {e}")
        return False


def clean_expired_cache():
    """清理过期的缓存文件"""
    try:
        if not os.path.exists(STOCK_DATA_DIR):
            return
        
        current_time = datetime.now()
        cleaned_count = 0
        
        for filename in os.listdir(STOCK_DATA_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(STOCK_DATA_DIR, filename)
                try:
                    # 检查文件修改时间
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if current_time - file_mtime > timedelta(hours=CACHE_TTL * 2):  # 超过2倍缓存时间才删除
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"删除过期缓存: {filename}")
                except Exception as e:
                    logger.error(f"删除缓存文件失败 {filename}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"清理完成，删除了 {cleaned_count} 个过期缓存文件")
        else:
            logger.info("没有发现过期的缓存文件")
            
    except Exception as e:
        logger.error(f"清理缓存时发生错误: {e}")


def get_historical_cache_path(ts_code):
    """获取历史数据缓存文件路径"""
    return os.path.join(HISTORICAL_DATA_DIR, f'{ts_code}_historical.json')


def is_historical_cache_valid(cache_path):
    """检查历史数据缓存是否有效"""
    if not os.path.exists(cache_path):
        return False
    
    try:
        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - file_mtime < timedelta(hours=HISTORICAL_CACHE_TTL)
    except:
        return False


def get_historical_financial_data(ts_code):
    """获取股票历史财务数据（过去5年，如果不足5年则获取所有可用数据）"""
    cache_path = get_historical_cache_path(ts_code)
    
    # 检查缓存
    if is_historical_cache_valid(cache_path):
        logger.info(f"从缓存读取历史数据 {ts_code}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    try:
        logger.info(f"从Tushare获取历史数据 {ts_code}")
        
        # 计算日期范围（过去5年）
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y%m%d')
        
        # 获取历史PE、PB数据（daily_basic接口）
        daily_data = pro.daily_basic(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields='ts_code,trade_date,pe,pe_ttm,pb'
        )
        
        # 获取历史ROE数据（fina_indicator接口，按季度）
        # 先获取可用的季度列表
        logger.info(f"获取 {ts_code} 的季度列表...")
        quarters_data = pro.fina_indicator(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields='ts_code,end_date'
        )
        
        if quarters_data.empty:
            logger.warning(f"未获取到 {ts_code} 的季度数据")
            quarters = []
        else:
            # 获取季度列表
            quarters = quarters_data['end_date'].tolist()
            quarters = sorted(list(set(quarters)), reverse=True)
            # 只取最近12个季度
            quarters = quarters[-12:]
            logger.info(f"获取到 {len(quarters)} 个季度: {quarters}")
        
        roe_data = []
        debt_to_asset_data = []
        gross_profit_margin_data = []
        
        for period in quarters:
            try:
                # 获取ROE和资产负债率数据
                logger.info(f"正在获取 {ts_code} {period} 季度财务指标数据...")
                fina_data = pro.fina_indicator(
                    ts_code=ts_code,
                    period=period,
                    fields='ts_code,end_date,roe,debt_to_assets'
                )
                if not fina_data.empty:
                    roe_value = fina_data.iloc[0]['roe']
                    debt_to_assets_value = fina_data.iloc[0]['debt_to_assets']
                    logger.info(f"获取到 {period} ROE: {roe_value}, 资产负债率: {debt_to_assets_value}")
                    
                    if roe_value is not None and not pd.isna(roe_value):
                        roe_data.append({
                            'period': period,
                            'end_date': fina_data.iloc[0]['end_date'],
                            'roe': roe_value
                        })
                    
                    if debt_to_assets_value is not None and not pd.isna(debt_to_assets_value):
                        debt_to_asset_data.append({
                            'period': period,
                            'end_date': fina_data.iloc[0]['end_date'],
                            'debt_to_assets': debt_to_assets_value
                        })
                else:
                    logger.warning(f"未获取到 {ts_code} {period} 季度财务指标数据")
                
                # 获取毛利率数据（从利润表）
                logger.info(f"正在获取 {ts_code} {period} 季度利润表数据...")
                income_data = pro.income(
                    ts_code=ts_code,
                    period=period,
                    fields='ts_code,end_date,revenue,oper_cost'
                )
                if not income_data.empty:
                    revenue = income_data.iloc[0]['revenue']
                    oper_cost = income_data.iloc[0]['oper_cost']
                    logger.info(f"获取到 {period} 营业收入: {revenue}, 营业成本: {oper_cost}")
                    
                    if revenue and oper_cost and revenue > 0 and not pd.isna(revenue) and not pd.isna(oper_cost):
                        gross_profit_margin = ((revenue - oper_cost) / revenue) * 100
                        gross_profit_margin_data.append({
                            'period': period,
                            'end_date': income_data.iloc[0]['end_date'],
                            'gross_profit_margin': gross_profit_margin
                        })
                        logger.info(f"计算得到 {period} 毛利率: {gross_profit_margin:.2f}%")
                    else:
                        logger.warning(f"{period} 营业收入或营业成本数据无效")
                else:
                    logger.warning(f"未获取到 {ts_code} {period} 季度利润表数据")
                        
            except Exception as e:
                logger.warning(f"获取 {ts_code} {period} 季度财务数据失败: {e}")
                continue
        
        # 处理数据，计算平均值
        historical_data = {
            'ts_code': ts_code,
            'pe_data': [],
            'pb_data': [],
            'roe_data': roe_data,
            'debt_to_asset_data': debt_to_asset_data,
            'gross_profit_margin_data': gross_profit_margin_data,
            'averages': {},
            'cache_time': datetime.now().isoformat()
        }
        
        # 处理PE、PB数据
        if not daily_data.empty:
            # 过滤掉空值和异常值
            pe_values = daily_data['pe'].dropna()
            pe_values = pe_values[(pe_values > 0) & (pe_values < 1000)]  # 过滤异常值
            
            pb_values = daily_data['pb'].dropna()
            pb_values = pb_values[(pb_values > 0) & (pb_values < 100)]  # 过滤异常值
            
            historical_data['pe_data'] = pe_values.tolist()
            historical_data['pb_data'] = pb_values.tolist()
            
            # 计算平均值
            if len(pe_values) > 0:
                historical_data['averages']['pe'] = float(pe_values.mean())
            if len(pb_values) > 0:
                historical_data['averages']['pb'] = float(pb_values.mean())
        
        # 处理ROE数据
        if roe_data:
            roe_values = [item['roe'] for item in roe_data if item['roe'] is not None]
            if roe_values:
                historical_data['averages']['roe'] = sum(roe_values) / len(roe_values)
        
        # 处理资产负债率数据
        if debt_to_asset_data:
            debt_values = [item['debt_to_assets'] for item in debt_to_asset_data if item['debt_to_assets'] is not None]
            if debt_values:
                historical_data['averages']['debt_to_asset_ratio'] = sum(debt_values) / len(debt_values)
        
        # 处理毛利率数据
        if gross_profit_margin_data:
            margin_values = [item['gross_profit_margin'] for item in gross_profit_margin_data if item['gross_profit_margin'] is not None]
            if margin_values:
                historical_data['averages']['gross_profit_margin'] = sum(margin_values) / len(margin_values)
        
        # 保存缓存
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(historical_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"历史数据获取成功: {ts_code}")
        return historical_data
        
    except Exception as e:
        logger.error(f"获取历史数据失败 {ts_code}: {e}")
        return None


def calculate_percentile_vs_history(current_value, historical_data, metric):
    """计算当前值相对于历史数据的百分位"""
    if not historical_data or metric not in historical_data.get('averages', {}):
        return None
    
    historical_avg = historical_data['averages'][metric]
    
    if historical_avg == 0:
        return None
    
    # 计算相对于历史平均值的比例
    ratio = current_value / historical_avg
    
    # 转换为百分位（0-100）
    if ratio >= 2.0:  # 当前值是历史平均值的2倍或以上
        percentile = 100
    elif ratio <= 0.5:  # 当前值是历史平均值的一半或以下
        percentile = 0
    else:
        # 线性映射：0.5-2.0 映射到 0-100
        percentile = (ratio - 0.5) / 1.5 * 100
    
    return {
        'percentile': round(percentile, 1),
        'ratio': round(ratio, 2),
        'current': current_value,
        'historical_avg': round(historical_avg, 2),
        'vs_avg': round((ratio - 1) * 100, 1)  # 相对于平均值的百分比差异
    }


def get_stock_basic_info(ts_code):
    """获取股票基本信息"""
    try:
        # 获取主营业务信息 - 增加重试机制
        business_info = {
            'main_business': '',
            'business_scope': '',
            'introduction': ''
        }
        
        try:
            basic_df = pro.stock_company(ts_code=ts_code, 
                                         fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province,city,website,email,office,business_scope,main_business,introduction')
            
            if not basic_df.empty:
                business_info = {
                    'main_business': basic_df.iloc[0].get('main_business', ''),
                    'business_scope': basic_df.iloc[0].get('business_scope', ''),
                    'introduction': basic_df.iloc[0].get('introduction', '')
                }
        except Exception as e:
            logger.warning(f"获取公司信息失败: {e}")
            # 使用概念信息作为降级策略
            try:
                concept_df = pro.concept_detail(ts_code=ts_code)
                if not concept_df.empty:
                    business_info['main_business'] = concept_df.iloc[0].get('concept_name', '')
            except Exception as e2:
                logger.warning(f"获取概念信息失败: {e2}")
        
        # 股票基础信息 - 增加重试机制
        stock_basic_df = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                stock_basic_df = pro.stock_basic(ts_code=ts_code, 
                                                fields='ts_code,symbol,name,area,industry,market,list_date')
                if not stock_basic_df.empty:
                    break
                else:
                    logger.warning(f"股票 {ts_code} 基础信息为空，尝试 {attempt + 1}/{max_retries}")
            except Exception as e:
                logger.warning(f"获取股票基础信息失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # 等待1秒后重试
        
        if stock_basic_df is None or stock_basic_df.empty:
            logger.error(f"无法获取股票 {ts_code} 的基础信息")
            return None
        
        basic_info = stock_basic_df.iloc[0].to_dict()
        
        # 获取最新交易日期（扩大查询范围到30天，确保能获取到最新交易日）
        trade_cal = pro.trade_cal(exchange='', is_open='1', 
                                  start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                                  end_date=datetime.now().strftime('%Y%m%d'))
        if trade_cal.empty:
            logger.error("无法获取交易日历")
            return None
        
        # 按日期排序，确保获取真正的最新交易日
        trade_cal = trade_cal.sort_values('cal_date')
        latest_trade_date = trade_cal.iloc[-1]['cal_date']
        prev_trade_date = trade_cal.iloc[-2]['cal_date'] if len(trade_cal) > 1 else latest_trade_date
        
        logger.info(f"获取到最新交易日: {latest_trade_date}, 前一交易日: {prev_trade_date}")
        
        # 获取最新价格
        daily_df = pro.daily(ts_code=ts_code, trade_date=latest_trade_date,
                            fields='close,pre_close,pct_chg')
        
        price_info = {}
        if not daily_df.empty:
            price_info = {
                'price': round(daily_df.iloc[0]['close'], 2),
                'pre_close': round(daily_df.iloc[0]['pre_close'], 2),
                'pct_chg': round(daily_df.iloc[0]['pct_chg'], 2)
            }
        else:
            price_info = {'price': 0, 'pre_close': 0, 'pct_chg': 0}
        
        # 获取市值数据
        daily_basic_df = pro.daily_basic(ts_code=ts_code, trade_date=latest_trade_date,
                                         fields='total_mv,circ_mv,pe,pb,total_share')
        market_info = {}
        total_share = 0
        if not daily_basic_df.empty:
            total_mv = daily_basic_df.iloc[0]['total_mv']
            total_share = daily_basic_df.iloc[0].get('total_share', 0)
            market_info = {
                'market_value': round(total_mv / 10000, 2) if total_mv else 0,  # 转换为亿元
                'pe': round(daily_basic_df.iloc[0]['pe'], 2) if daily_basic_df.iloc[0]['pe'] else 0,
                'pb': round(daily_basic_df.iloc[0]['pb'], 2) if daily_basic_df.iloc[0]['pb'] else 0
            }
        else:
            market_info = {'market_value': 0, 'pe': 0, 'pb': 0}
        
        # 获取股东数据
        holder_info = {'holder_num': 0, 'holder_avg_amount': 0}
        try:
            # 获取最近的股东数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
            holder_df = pro.stk_holdernumber(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if not holder_df.empty:
                # 取最新的数据
                latest_holder = holder_df.iloc[0]
                holder_num = latest_holder.get('holder_num', 0)
                
                if holder_num and holder_num > 0 and total_share and total_share > 0:
                    # 计算平均每个股东持股数量
                    avg_shares = total_share / holder_num
                    # 计算平均持股金额（股数 × 股价）
                    avg_amount = avg_shares * price_info.get('price', 0)
                    
                    holder_info = {
                        'holder_num': int(holder_num),
                        'holder_avg_amount': round(avg_amount, 2)
                    }
        except Exception as e:
            logger.warning(f"获取股东数据失败: {e}")
        
        # 获取财务数据（ROE、毛利率、资产负债率）- 使用最新报告期
        roe = 0
        gross_profit_margin = 0
        debt_to_asset_ratio = 0
        
        try:
            # 获取最近的财务指标数据
            current_year = datetime.now().year
            periods = [f'{current_year}0930', f'{current_year}0630', f'{current_year}0331', 
                      f'{current_year-1}1231', f'{current_year-1}0930']
            
            for period in periods:
                # 获取ROE和资产负债率
                fina_df = pro.fina_indicator(ts_code=ts_code, period=period, fields='roe,debt_to_assets')
                if not fina_df.empty:
                    if fina_df.iloc[0]['roe'] and roe == 0:
                        roe = round(fina_df.iloc[0]['roe'], 2)
                    if fina_df.iloc[0]['debt_to_assets'] and debt_to_asset_ratio == 0:
                        debt_to_asset_ratio = round(fina_df.iloc[0]['debt_to_assets'], 2)
                
                # 获取毛利率（从利润表）
                income_df = pro.income(ts_code=ts_code, period=period, fields='revenue,oper_cost')
                if not income_df.empty and gross_profit_margin == 0:
                    revenue = income_df.iloc[0]['revenue']
                    oper_cost = income_df.iloc[0]['oper_cost']
                    if revenue and oper_cost and revenue > 0:
                        gross_profit_margin = round(((revenue - oper_cost) / revenue) * 100, 2)
                
                # 如果所有数据都获取到了，就退出循环
                if roe != 0 and gross_profit_margin != 0 and debt_to_asset_ratio != 0:
                    break
                    
        except Exception as e:
            logger.warning(f"获取财务数据失败: {e}")
        
        return {
            'basic': basic_info,
            'business': business_info,
            'price': price_info,
            'market': market_info,
            'holder': holder_info,
            'financial': {
                'roe': roe,
                'pe': market_info['pe'],
                'pb': market_info['pb'],
                'gross_profit_margin': gross_profit_margin,
                'debt_to_asset_ratio': debt_to_asset_ratio
            },
            'trade_date': latest_trade_date
        }
    except Exception as e:
        logger.error(f"获取股票 {ts_code} 基本信息失败: {e}")
        return None




def get_stock_data(ts_code):
    """获取股票完整数据（24小时缓存优先策略）"""
    cache_path = get_stock_cache_path(ts_code)
    
    # 优先检查24小时内的缓存
    if is_cache_valid(cache_path):
        logger.info(f"从24小时缓存读取 {ts_code}")
        with open(cache_path, 'r', encoding='utf-8') as f:
            cached_data = json.load(f)
            cached_data['from_cache'] = True
            return cached_data
    
    # 缓存过期或不存在，从Tushare API获取
    logger.info(f"缓存过期，从Tushare API获取 {ts_code}")
    stock_info = get_stock_basic_info(ts_code)
    
    if stock_info is None:
        logger.error(f"Tushare API获取失败: {ts_code}")
        # 如果API失败，检查是否有过期缓存可用
        if os.path.exists(cache_path):
            logger.info(f"API失败，使用过期缓存 {ts_code}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                cached_data['from_cache'] = True
                cached_data['cache_expired'] = True
                return cached_data
        else:
            # 完全无法获取数据
            return None
    
    # 获取历史数据用于进度条比较
    historical_data = get_historical_financial_data(ts_code)
    
    # 计算历史比较数据
    historical_comparison = {}
    if historical_data and stock_info['financial']:
        # ROE历史比较
        if 'roe' in stock_info['financial'] and stock_info['financial']['roe'] is not None:
            roe_comparison = calculate_percentile_vs_history(
                stock_info['financial']['roe'], historical_data, 'roe'
            )
            if roe_comparison:
                historical_comparison['roe'] = roe_comparison
        
        # PE历史比较
        if 'pe' in stock_info['financial'] and stock_info['financial']['pe'] is not None:
            pe_comparison = calculate_percentile_vs_history(
                stock_info['financial']['pe'], historical_data, 'pe'
            )
            if pe_comparison:
                historical_comparison['pe'] = pe_comparison
        
        # PB历史比较
        if 'pb' in stock_info['financial'] and stock_info['financial']['pb'] is not None:
            pb_comparison = calculate_percentile_vs_history(
                stock_info['financial']['pb'], historical_data, 'pb'
            )
            if pb_comparison:
                historical_comparison['pb'] = pb_comparison
        
        # 毛利率历史比较
        if 'gross_profit_margin' in stock_info['financial'] and stock_info['financial']['gross_profit_margin'] is not None:
            margin_comparison = calculate_percentile_vs_history(
                stock_info['financial']['gross_profit_margin'], historical_data, 'gross_profit_margin'
            )
            if margin_comparison:
                historical_comparison['gross_profit_margin'] = margin_comparison
        
        # 资产负债率历史比较
        if 'debt_to_asset_ratio' in stock_info['financial'] and stock_info['financial']['debt_to_asset_ratio'] is not None:
            debt_comparison = calculate_percentile_vs_history(
                stock_info['financial']['debt_to_asset_ratio'], historical_data, 'debt_to_asset_ratio'
            )
            if debt_comparison:
                historical_comparison['debt_to_asset_ratio'] = debt_comparison
    
    # 构建完整数据
    data = {
        'code': stock_info['basic']['symbol'],
        'ts_code': ts_code,
        'name': stock_info['basic']['name'],
        'price': stock_info['price']['price'],
        'pct_chg': stock_info['price']['pct_chg'],
        'market_value': stock_info['market']['market_value'],
        'industry': stock_info['basic']['industry'],
        'area': stock_info['basic']['area'],
        'list_date': stock_info['basic']['list_date'],
        'financial': stock_info['financial'],
        'holder': stock_info['holder'],
        'main_business': stock_info['business'].get('main_business', ''),
        'business_scope': stock_info['business'].get('business_scope', ''),
        'introduction': stock_info['business'].get('introduction', ''),
        'logo_url': f'https://gushitong.baidu.com/stock/logo/{stock_info["basic"]["symbol"]}.png',
        'historical_comparison': historical_comparison,  # 新增历史比较数据
        'cached_time': datetime.now().isoformat(),
        'from_cache': False
    }
    
    # 保存新缓存
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已缓存股票数据: {ts_code}")
    except Exception as e:
        logger.error(f"保存缓存失败: {e}")
    
    return data


@app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/random-stock')
def random_stock():
    """获取随机股票（24小时缓存优先策略）"""
    try:
        # 获取已浏览的股票列表
        viewed = request.args.get('viewed', '')
        viewed_list = viewed.split(',') if viewed else []
        
        # 获取股票列表
        stocks = get_stock_list()
        if not stocks:
            return jsonify({'error': '无法获取股票列表'}), 500
        
        # 过滤已浏览的股票
        available_stocks = [s for s in stocks if s['ts_code'] not in viewed_list]
        
        if not available_stocks:
            return jsonify({'error': '所有股票已浏览完毕', 'all_viewed': True}), 404
        
        # 尝试获取股票数据，最多尝试10次
        max_attempts = 10
        attempts = 0
        
        while attempts < max_attempts and available_stocks:
            # 随机选择一只
            selected = random.choice(available_stocks)
            ts_code = selected['ts_code']
            
            # 获取详细数据
            stock_data = get_stock_data(ts_code)
            
            if stock_data is not None:
                # 成功获取数据
                return jsonify(stock_data)
            else:
                # 获取失败，从可用列表中移除这只股票，尝试下一只
                logger.warning(f"无法获取股票 {ts_code} 的数据，尝试下一只")
                available_stocks.remove(selected)
                attempts += 1
        
        # 所有尝试都失败了
        return jsonify({'error': '暂时无法获取股票数据，请稍后重试'}), 503
    
    except Exception as e:
        logger.error(f"获取随机股票失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stock/<ts_code>')
def get_stock(ts_code):
    """获取指定股票数据"""
    try:
        stock_data = get_stock_data(ts_code)
        
        if stock_data is None:
            return jsonify({'error': f'股票 {ts_code} 不存在或数据获取失败'}), 404
        
        stock_data['from_cache'] = is_cache_valid(get_stock_cache_path(ts_code))
        
        return jsonify(stock_data)
    
    except Exception as e:
        logger.error(f"获取股票 {ts_code} 失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def stats():
    """获取统计信息"""
    try:
        stocks = get_stock_list()
        cached_stocks = len([f for f in os.listdir(STOCK_DATA_DIR) if f.endswith('.json')])
        
        return jsonify({
            'total_stocks': len(stocks),
            'cached_stocks': cached_stocks,
            'cache_hit_rate': round(cached_stocks / len(stocks) * 100, 2) if stocks else 0
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 启动时清理过期缓存
    logger.info("启动应用，清理过期缓存...")
    clean_expired_cache()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

