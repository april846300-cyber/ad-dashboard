import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# 페이지 설정
# ======================
st.set_page_config(layout="wide")

# ======================
# 데이터 로드
# ======================
@st.cache_data
def load_monthly():
    df = pd.read_csv("월별_캠페인_광고리포트_수정.csv")
    df.columns = df.columns.str.strip()

    # 연도 생성
    df['연도'] = df['월'].astype(str).str[:4]

    num_cols = [
        '총비용(VAT포함,원)',
        '노출수',
        '클릭수',
        '전환수',
        '전환매출액(원)'
    ]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 광고그룹 기준 KPI 계산
    df['ROAS'] = ((df['전환매출액(원)'] / df['총비용(VAT포함,원)']) * 100).replace([float('inf')],0)
    df['CTR'] = ((df['클릭수'] / df['노출수']) * 100).replace([float('inf')],0)
    df['CVR'] = ((df['전환수'] / df['클릭수']) * 100).replace([float('inf')],0)

    return df


monthly = load_monthly()

# ======================
# 타이틀
# ======================
st.title("전체 광고 현황 정리")

# ======================
# 사이드바 필터 (캠페인 → 광고그룹)
# ======================
st.sidebar.header("필터 설정")

# 전체 데이터 사용 (캠페인 유형 전체)
filtered = monthly.copy()

# 캠페인 선택 (전체 옵션 추가)
campaign_list = ['전체'] + sorted(filtered['캠페인'].unique().tolist())
campaign = st.sidebar.selectbox(
    "캠페인 선택",
    campaign_list
)

# 캠페인 필터링
if campaign == '전체':
    data = filtered.copy()
else:
    data = filtered[filtered['캠페인'] == campaign]

# 광고그룹 선택 (전체 옵션 추가)
ad_group_list = ['전체'] + sorted(data['광고그룹'].unique().tolist())
ad_group = st.sidebar.selectbox(
    "광고그룹 선택",
    ad_group_list
)

# 광고그룹 필터링
if ad_group == '전체':
    final_data = data.copy()
else:
    final_data = data[data['광고그룹'] == ad_group]

# 사이드바에 현재 선택 상태 표시
st.sidebar.markdown("---")
st.sidebar.markdown("### 현재 선택")
st.sidebar.info(f"**캠페인:** {campaign}\n\n**광고그룹:** {ad_group}")

# ======================
# 메인 컨텐츠 시작
# ======================
st.subheader("평균 KPI(2025년)")

# ======================
# KPI 카드 (전체 합계 기준)
# ======================
# 전체 합계로 KPI 계산
total_cost = final_data['총비용(VAT포함,원)'].sum()
total_revenue = final_data['전환매출액(원)'].sum()
total_impressions = final_data['노출수'].sum()
total_clicks = final_data['클릭수'].sum()
total_conversions = final_data['전환수'].sum()

# 전체 합계 기준 KPI
if total_cost > 0:
    overall_roas = (total_revenue / total_cost) * 100
else:
    overall_roas = 0

if total_impressions > 0:
    overall_ctr = (total_clicks / total_impressions) * 100
else:
    overall_ctr = 0

if total_clicks > 0:
    overall_cvr = (total_conversions / total_clicks) * 100
else:
    overall_cvr = 0

col1, col2, col3 = st.columns(3)

col1.metric("ROAS", f"{overall_roas:.1f}%")
col2.metric("CTR", f"{overall_ctr:.2f}%")
col3.metric("CVR", f"{overall_cvr:.2f}%")

# ======================
# 월 KPI 집계 (광고그룹 → 월 합산)
# ======================
if campaign == '전체' and ad_group == '전체':
    group_cols = ['월']
elif campaign != '전체' and ad_group == '전체':
    group_cols = ['월', '캠페인']
else:
    group_cols = ['월', '캠페인', '광고그룹']

monthly_group = final_data.groupby(
    group_cols,
    as_index=False
).agg({
    '총비용(VAT포함,원)': 'sum',
    '노출수': 'sum',
    '클릭수': 'sum',
    '전환수': 'sum',
    '전환매출액(원)': 'sum'
})

monthly_group['ROAS'] = ((monthly_group['전환매출액(원)'] / monthly_group['총비용(VAT포함,원)']) * 100).replace([float('inf')], 0)
monthly_group['CTR'] = ((monthly_group['클릭수'] / monthly_group['노출수']) * 100).replace([float('inf')], 0)
monthly_group['CVR'] = ((monthly_group['전환수'] / monthly_group['클릭수']) * 100).replace([float('inf')], 0)

plot_df = monthly_group.melt(
    id_vars=['월'],
    value_vars=['ROAS', 'CTR', 'CVR'],
    var_name='지표',
    value_name='값'
)

fig = px.line(
    plot_df,
    x='월',
    y='값',
    color='지표',
    markers=True,
    title='월별 KPI 추이 (%)'
)

fig.update_yaxes(ticksuffix="%")

st.plotly_chart(fig, use_container_width=True)


st.write("")
st.write("")

# ======================
# 캠페인별 광고그룹별 월별 합계 데이터
# ======================
st.subheader("월별 캠페인·광고그룹 성과")

# 캠페인, 광고그룹, 월별로 합계
detail_group = final_data.groupby(
    ['월', '캠페인', '광고그룹'],
    as_index=False
).agg({
    '총비용(VAT포함,원)': 'sum',
    '노출수': 'sum',
    '클릭수': 'sum',
    '전환수': 'sum',
    '전환매출액(원)': 'sum'
})

detail_group['ROAS'] = ((detail_group['전환매출액(원)'] / detail_group['총비용(VAT포함,원)']) * 100).replace([float('inf')], 0)
detail_group['CTR'] = ((detail_group['클릭수'] / detail_group['노출수']) * 100).replace([float('inf')], 0)
detail_group['CVR'] = ((detail_group['전환수'] / detail_group['클릭수']) * 100).replace([float('inf')], 0)

display_df = detail_group.copy()

# 정렬: 월 → 캠페인 → 광고그룹
display_df = display_df.sort_values(['월', '캠페인', '광고그룹'])

# 숫자 포맷팅
for col in ['총비용(VAT포함,원)', '노출수', '클릭수', '전환수', '전환매출액(원)']:
    display_df[col] = display_df[col].apply(lambda x: f'{int(x):,}')

for col in ['ROAS', 'CTR', 'CVR']:
    display_df[col] = display_df[col].map('{:.2f}%'.format)

st.dataframe(display_df, use_container_width=True, height=600)


st.write("")
st.write("")

# ======================
# 연도별 집계 (광고그룹 기준 → 연도 합산)
# ======================
st.subheader("연도별 캠페인·광고그룹 성과")

yearly = monthly.groupby(
    ['연도', '캠페인', '광고그룹'],
    as_index=False
).agg({
    '총비용(VAT포함,원)': 'sum',
    '노출수': 'sum',
    '클릭수': 'sum',
    '전환수': 'sum',
    '전환매출액(원)': 'sum'
})

yearly['ROAS'] = ((yearly['전환매출액(원)'] / yearly['총비용(VAT포함,원)']) * 100).replace([float('inf')], 0)
yearly['CTR'] = ((yearly['클릭수'] / yearly['노출수']) * 100).replace([float('inf')], 0)
yearly['CVR'] = ((yearly['전환수'] / yearly['클릭수']) * 100).replace([float('inf')], 0)

year_display = yearly.copy()

# 숫자 포맷팅
for col in ['총비용(VAT포함,원)', '노출수', '클릭수', '전환수', '전환매출액(원)']:
    year_display[col] = year_display[col].apply(lambda x: f'{int(x):,}')

for col in ['ROAS', 'CTR', 'CVR']:
    year_display[col] = year_display[col].map('{:.2f}%'.format)

st.dataframe(year_display, use_container_width=True, height=600)


st.write("")
st.write("")

# ======================
# 연도별 캠페인 합산 데이터 (광고그룹 무시)
# ======================
st.subheader("연도별 캠페인 성과(광고그룹 통합)")

yearly_campaign = monthly.groupby(
    ['연도', '캠페인'],
    as_index=False
).agg({
    '총비용(VAT포함,원)': 'sum',
    '노출수': 'sum',
    '클릭수': 'sum',
    '전환수': 'sum',
    '전환매출액(원)': 'sum'
})

yearly_campaign['ROAS'] = ((yearly_campaign['전환매출액(원)'] / yearly_campaign['총비용(VAT포함,원)']) * 100).replace([float('inf')], 0)
yearly_campaign['CTR'] = ((yearly_campaign['클릭수'] / yearly_campaign['노출수']) * 100).replace([float('inf')], 0)
yearly_campaign['CVR'] = ((yearly_campaign['전환수'] / yearly_campaign['클릭수']) * 100).replace([float('inf')], 0)

year_campaign_display = yearly_campaign.copy()

# 숫자 포맷팅
for col in ['총비용(VAT포함,원)', '노출수', '클릭수', '전환수', '전환매출액(원)']:
    year_campaign_display[col] = year_campaign_display[col].apply(lambda x: f'{int(x):,}')

for col in ['ROAS', 'CTR', 'CVR']:
    year_campaign_display[col] = year_campaign_display[col].map('{:.2f}%'.format)

st.dataframe(year_campaign_display, use_container_width=True, height=600)