import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# 페이지 설정 (전체폭)
# ======================
st.set_page_config(layout="wide")

# ======================
# 데이터 로드
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("월별_캠페인_광고리포트.csv")

    # 숫자형 변환 (혹시 모를 오류 대비)
    num_cols = [
        '총비용(VAT포함,원)',
        '노출수',
        '클릭수',
        '전환수',
        '전환매출액(원)'
    ]

    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # KPI 계산 (% 기준)
    df['ROAS'] = ((df['전환매출액(원)'] / df['총비용(VAT포함,원)']) * 100).replace([float('inf')],0)
    df['CTR'] = ((df['클릭수'] / df['노출수']) * 100).replace([float('inf')],0)
    df['CVR'] = ((df['전환수'] / df['클릭수']) * 100).replace([float('inf')],0)

    return df

monthly = load_data()

# ======================
# 타이틀
# ======================
st.title("광고 캠페인 대시보드")

# ======================
# 캠페인 선택
# ======================
campaign = st.selectbox("캠페인 선택", monthly['캠페인'].unique())

data = monthly[monthly['캠페인']==campaign]

# ======================
# KPI 카드
# ======================
col1,col2,col3 = st.columns(3)

col1.metric("평균 ROAS", f"{data['ROAS'].mean():.1f}%")
col2.metric("평균 CTR", f"{data['CTR'].mean():.2f}%")
col3.metric("평균 CVR", f"{data['CVR'].mean():.2f}%")

# ======================
# 그래프용 변환
# ======================
plot_df = data.melt(
    id_vars=['월'],
    value_vars=['ROAS','CTR','CVR'],
    var_name='지표',
    value_name='값'
)

# ======================
# KPI 통합 그래프
# ======================
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
# 테이블 출력 (% 표시)
# ======================
st.subheader("월별 상세 데이터")

display_df = data.copy()

for col in ['ROAS','CTR','CVR']:
    display_df[col] = display_df[col].map('{:.2f}%'.format)

st.dataframe(
    display_df,
    use_container_width=True,
    height=600
)
