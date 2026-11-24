# ===== 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== 페이지 기본 설정 =====
st.set_page_config(page_title="Titanic 대시보드", layout="wide")  # [추가]

# ===== 데이터 불러오기 함수 =====
@st.cache_data
def load_data():
    # titanic.csv 파일을 읽어 반환 (캐싱으로 재실행 시 속도 향상)
    return pd.read_csv("titanic.csv")

# ===== 데이터 필터링 및 KPI 함수 =====
def filter_data(df, sexes, classes, age_range):
    # age_range 튜플에서 최소·최대 나이 추출
    min_age, max_age = age_range
    
    # 성별, 객실 등급, 나이 범위 조건 생성
    cond_sex = df["sex"].isin(sexes)
    cond_class = df["pclass"].isin(classes)
    cond_age = df["age"].between(min_age, max_age)
    
    # 세 조건을 모두 만족하는 행만 반환
    return df[cond_sex & cond_class & cond_age]

def kpi(df):
    # 데이터가 비어있으면 (0, 0, 0) 반환
    if df.empty:
        return (0, 0, 0)
    
    passenger_count = len(df)
    survival_rate = round(df["survived"].mean() * 100, 1)
    mean_age = df["age"].mean()
    avg_age = round(mean_age, 1) if pd.notna(mean_age) else 0
    
    return (passenger_count, survival_rate, avg_age)

# ===== 시각화 차트 함수 =====
def class_rate_bar(df):
    # 객실 등급별 평균 생존율(%) 계산
    rate_df = (df.groupby("pclass", as_index=False)["survived"]
                 .mean()
                 .assign(survival_rate=lambda x: (x["survived"] * 100).round(1)))
    
    fig = px.bar(
        rate_df,
        x="pclass",
        y="survival_rate",
        text="survival_rate",
        title="객실 등급별 생존율 (%)",
        labels={"pclass": "객실 등급", "survival_rate": "생존율 (%)"}
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_xaxes(type="category")
    fig.update_yaxes(range=[0, 110])
    
    return fig

def age_hist(df):
    # 생존 여부(0, 1)를 한글 라벨로 변환
    temp_df = df.copy()
    temp_df["생존여부"] = temp_df["survived"].map({0: "사망", 1: "생존"})
    
    fig = px.histogram(
        temp_df,
        x="age",
        color="생존여부",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 나이 분포",
        labels={"age": "나이", "count": "승객 수"}
    )
    
    return fig

# ===== 메인 제목 및 데이터 로드 =====
st.title("타이타닉, 누가 살아남았나?")
df = load_data()

# ===== 사이드바 필터 설정 =====
st.sidebar.header("필터 조건")

# 성별 다중 선택 (기본값: 전체 선택)
selected_sexes = st.sidebar.multiselect(
    "성별 선택",
    options=["male", "female"],
    default=["male", "female"]
)

# 객실 등급 다중 선택 (기본값: 전체 선택)
selected_classes = st.sidebar.multiselect(
    "객실 등급 선택",
    options=[1, 2, 3],
    default=[1, 2, 3]
)

# 나이 범위 슬라이더 (0~80세)
selected_age_range = st.sidebar.slider(
    "나이 범위 선택",
    min_value=0,
    max_value=80,
    value=(0, 80)
)

# ===== 본문 영역 =====
# 사이드바 조건에 맞게 데이터 필터링
filtered_df = filter_data(df, selected_sexes, selected_classes, selected_age_range)

# KPI 지표 계산 (승객 수, 생존율, 평균 나이)
count, rate, avg_age = kpi(filtered_df)

# 3개의 열로 나누어 KPI 숫자 카드 표시
col1, col2, col3 = st.columns(3)
col1.metric("승객 수", f"{count}명")
col2.metric("생존율", f"{rate}%")
col3.metric("평균 나이", f"{avg_age}세")

# KPI 아래 2개의 열로 나누어 차트 배치  # [추가]
chart_col1, chart_col2 = st.columns(2)  # [추가]
with chart_col1:  # [추가]
    st.plotly_chart(class_rate_bar(filtered_df), use_container_width=True)  # [추가]
with chart_col2:  # [추가]
    st.plotly_chart(age_hist(filtered_df), use_container_width=True)  # [추가]

# 맨 아래 접이식 영역에 필터링된 데이터 표 표시  # [추가]
with st.expander("데이터 보기"):  # [추가]
    st.dataframe(filtered_df, use_container_width=True)  # [추가]
