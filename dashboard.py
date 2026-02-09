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
    df = pd.read_csv("월별_캠페인_광고리포트.csv")
    df.columns = df.columns.str.strip()

    # 👉 연도 생성 (월 컬럼에서 추출)
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

    # KPI 계산 (%)
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
# 캠페인 월 KPI 분석
# ======================
st.subheader("캠페인별 월 KPI 추이 분석")

campaign = st.selectbox("캠페인 선택", monthly['캠페인'].unique())

data = monthly[monthly['캠페인']==campaign]

# KPI 카드
col1,col2,col3 = st.columns(3)

col1.metric("평균 ROAS", f"{data['ROAS'].mean():.1f}%")
col2.metric("평균 CTR", f"{data['CTR'].mean():.2f}%")
col3.metric("평균 CVR", f"{data['CVR'].mean():.2f}%")

# ======================
# KPI 그래프
# ======================
plot_df = data.melt(
    id_vars=['월'],
    value_vars=['ROAS','CTR','CVR'],
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

# ======================
# 월별 상세 데이터
# ======================
st.subheader("캠페인 월별 상세 데이터")

display_df = data.copy()

for col in ['ROAS','CTR','CVR']:
    display_df[col] = display_df[col].map('{:.2f}%'.format)

st.dataframe(
    display_df,
    use_container_width=True,
    height=600
)

# ======================
# 연도별 상세 데이터 (월 데이터 합산 생성)
# ======================
st.subheader("캠페인 연도별 상세 데이터 (월별 합산 기준)")

yearly = monthly.groupby(
    ['연도','캠페인'],
    as_index=False
).agg({
    '총비용(VAT포함,원)':'sum',
    '노출수':'sum',
    '클릭수':'sum',
    '전환수':'sum',
    '전환매출액(원)':'sum'
})

# KPI 다시 계산
yearly['ROAS'] = ((yearly['전환매출액(원)'] / yearly['총비용(VAT포함,원)']) * 100).replace([float('inf')],0)
yearly['CTR'] = ((yearly['클릭수'] / yearly['노출수']) * 100).replace([float('inf')],0)
yearly['CVR'] = ((yearly['전환수'] / yearly['클릭수']) * 100).replace([float('inf')],0)

year_display = yearly.copy()

for col in ['ROAS','CTR','CVR']:
    year_display[col] = year_display[col].map('{:.2f}%'.format)

st.dataframe(
    year_display,
    use_container_width=True,
    height=600
)
