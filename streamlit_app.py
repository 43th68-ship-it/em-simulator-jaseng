import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.fields.electric import PointCharge, ElectricField

st.set_page_config(
    page_title="전자기장 시뮬레이터",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ 전자기장 시뮬레이터")
st.caption("점전하 배치 → 3D 전기장 시각화 → 임의 지점 E 벡터 계산 · 대전과학고 자율생성 탐구활동 2026")

CM_TO_M = 0.01
NC_TO_C = 1e-9

if "charges" not in st.session_state:
    st.session_state.charges = [
        {"q": 1.0, "x": -1.0, "y": 0.0, "z": 0.0},
        {"q": -1.0, "x": 1.0, "y": 0.0, "z": 0.0},
    ]

# ── 사이드바 ─────────────────────────────
with st.sidebar:
    st.header("① 점전하 배치")
    st.caption("전하량: nC · 위치: cm")

    to_remove = None
    for i, c in enumerate(st.session_state.charges):
        with st.container(border=True):
            head = st.columns([3, 1])
            sym = "🔴" if c["q"] > 0 else "🔵" if c["q"] < 0 else "⚪"
            head[0].markdown(f"{sym} **전하 {i+1}**")
            if head[1].button("×", key=f"del_{i}"):
                to_remove = i
            c["q"] = st.number_input(
                "q [nC]", value=float(c["q"]), step=0.5,
                key=f"q_{i}", format="%.2f",
            )
            xyz = st.columns(3)
            c["x"] = xyz[0].number_input("x [cm]", value=float(c["x"]), step=0.5, key=f"x_{i}", format="%.2f")
            c["y"] = xyz[1].number_input("y [cm]", value=float(c["y"]), step=0.5, key=f"y_{i}", format="%.2f")
            c["z"] = xyz[2].number_input("z [cm]", value=float(c["z"]), step=0.5, key=f"z_{i}", format="%.2f")

    if to_remove is not None:
        st.session_state.charges.pop(to_remove)
        st.rerun()

    if st.button("＋ 전하 추가", use_container_width=True, type="primary"):
        st.session_state.charges.append({"q": 1.0, "x": 0.0, "y": 0.0, "z": 0.0})
        st.rerun()

    st.divider()
    st.caption("빠른 프리셋")
    ps = st.columns(3)
    if ps[0].button("다이폴", use_container_width=True):
        st.session_state.charges = [
            {"q": 1.0, "x": -1.0, "y": 0.0, "z": 0.0},
            {"q": -1.0, "x": 1.0, "y": 0.0, "z": 0.0},
        ]
        st.rerun()
    if ps[1].button("4극자", use_container_width=True):
        st.session_state.charges = [
            {"q": 1.0, "x": -1.0, "y": -1.0, "z": 0.0},
            {"q": -1.0, "x": 1.0, "y": -1.0, "z": 0.0},
            {"q": 1.0, "x": 1.0, "y": 1.0, "z": 0.0},
            {"q": -1.0, "x": -1.0, "y": 1.0, "z": 0.0},
        ]
        st.rerun()
    if ps[2].button("초기화", use_container_width=True):
        st.session_state.charges = [{"q": 1.0, "x": 0.0, "y": 0.0, "z": 0.0}]
        st.rerun()

    st.divider()
    st.header("② 쿼리 지점")
    st.caption("이 지점의 E 벡터를 계산·강조")
    qc = st.columns(3)
    qx = qc[0].number_input("x [cm]", value=0.0, step=0.5, format="%.2f", key="qx_in")
    qy = qc[1].number_input("y [cm]", value=2.0, step=0.5, format="%.2f", key="qy_in")
    qz = qc[2].number_input("z [cm]", value=0.0, step=0.5, format="%.2f", key="qz_in")

    with st.expander("③ 시각화 설정"):
        grid_n = st.slider("격자 밀도 (한 축당)", 6, 18, 10)
        box_size = st.slider("표시 영역 ±cm", 2, 10, 5)
        field_opacity = st.slider("배경 필드 진하기", 0.05, 1.0, 0.35, step=0.05)

# ── 물리 계산 ───────────────────────────
field = ElectricField([
    PointCharge(c["q"] * NC_TO_C,
                [c["x"]*CM_TO_M, c["y"]*CM_TO_M, c["z"]*CM_TO_M])
    for c in st.session_state.charges
])

L = box_size * CM_TO_M
xs = np.linspace(-L, L, grid_n)
X, Y, Z = np.meshgrid(xs, xs, xs, indexing="ij")
R = np.stack([X, Y, Z], axis=-1)

if len(st.session_state.charges) > 0:
    E = field.evaluate(R)
else:
    E = np.zeros_like(R)

Ex, Ey, Ez = E[..., 0], E[..., 1], E[..., 2]
mag = np.sqrt(Ex**2 + Ey**2 + Ez**2)

if mag.max() > 0:
    cap = np.percentile(mag[mag > 0], 85)
    scale = np.minimum(mag, cap) / (mag + 1e-30)
    Ex_c, Ey_c, Ez_c = Ex*scale, Ey*scale, Ez*scale
else:
    Ex_c, Ey_c, Ez_c = Ex, Ey, Ez

q_pos = np.array([qx*CM_TO_M, qy*CM_TO_M, qz*CM_TO_M])
E_query = field.evaluate(q_pos) if len(st.session_state.charges) > 0 else np.zeros(3)
E_mag = np.linalg.norm(E_query)
E_dir = E_query / E_mag if E_mag > 0 else np.zeros(3)

# ── 메인 ────────────────────────────────
col_viz, col_result = st.columns([3, 1])

with col_result:
    st.subheader("📍 쿼리 지점 결과")
    st.metric("|E|", f"{E_mag:.3e} V/m")

    st.markdown("**E 벡터** [V/m]")
    st.code(f"Ex = {E_query[0]:+.3e}\nEy = {E_query[1]:+.3e}\nEz = {E_query[2]:+.3e}")

    st.markdown("**방향 (단위벡터)**")
    st.code(f"x: {E_dir[0]:+.4f}\ny: {E_dir[1]:+.4f}\nz: {E_dir[2]:+.4f}")

    if E_mag > 0:
        theta = np.degrees(np.arccos(np.clip(E_dir[2], -1, 1)))
        phi = np.degrees(np.arctan2(E_dir[1], E_dir[0]))
        st.markdown("**구면좌표 방향**")
        st.code(f"θ (z축과) = {theta:.2f}°\nφ (xy면)  = {phi:.2f}°")

    st.divider()
    st.caption(f"현재 배치: 전하 {len(st.session_state.charges)}개")

with col_viz:
    fig = go.Figure()

    if len(st.session_state.charges) > 0 and mag.max() > 0:
        fig.add_trace(go.Cone(
            x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
            u=Ex_c.flatten(), v=Ey_c.flatten(), w=Ez_c.flatten(),
            sizemode="absolute", sizeref=L*0.06,
            colorscale=[[0, "rgba(180,180,220,0.4)"], [1, "rgba(94,58,168,1)"]],
            showscale=False,
            opacity=field_opacity,
            name="전기장",
            hoverinfo="skip",
        ))

    pos_ch = [c for c in st.session_state.charges if c["q"] > 0]
    neg_ch = [c for c in st.session_state.charges if c["q"] < 0]

    if pos_ch:
        fig.add_trace(go.Scatter3d(
            x=[c["x"]*CM_TO_M for c in pos_ch],
            y=[c["y"]*CM_TO_M for c in pos_ch],
            z=[c["z"]*CM_TO_M for c in pos_ch],
            mode="markers+text",
            marker=dict(size=[max(10, min(24, abs(c["q"])*6+8)) for c in pos_ch],
                        color="#E74C3C", line=dict(color="white", width=2)),
            text=[f"+{c['q']:.1f}nC" for c in pos_ch],
            textposition="top center",
            textfont=dict(color="#E74C3C", size=11),
            name="양전하",
        ))
    if neg_ch:
        fig.add_trace(go.Scatter3d(
            x=[c["x"]*CM_TO_M for c in neg_ch],
            y=[c["y"]*CM_TO_M for c in neg_ch],
            z=[c["z"]*CM_TO_M for c in neg_ch],
            mode="markers+text",
            marker=dict(size=[max(10, min(24, abs(c["q"])*6+8)) for c in neg_ch],
                        color="#3498DB", line=dict(color="white", width=2)),
            text=[f"{c['q']:.1f}nC" for c in neg_ch],
            textposition="top center",
            textfont=dict(color="#3498DB", size=11),
            name="음전하",
        ))

    fig.add_trace(go.Scatter3d(
        x=[q_pos[0]], y=[q_pos[1]], z=[q_pos[2]],
        mode="markers+text",
        marker=dict(size=12, color="#FFD700", symbol="diamond",
                    line=dict(color="black", width=2)),
        text=[f"쿼리 ({qx:.1f}, {qy:.1f}, {qz:.1f}) cm"],
        textposition="bottom center",
        textfont=dict(color="#DAA520", size=11),
        name="쿼리 지점",
    ))

    if E_mag > 0:
        arrow_len = L * 0.4
        tip = q_pos + E_dir * arrow_len
        fig.add_trace(go.Scatter3d(
            x=[q_pos[0], tip[0]], y=[q_pos[1], tip[1]], z=[q_pos[2], tip[2]],
            mode="lines",
            line=dict(color="#FF8C00", width=8),
            name="쿼리 지점 E 벡터",
        ))
        fig.add_trace(go.Cone(
            x=[tip[0]], y=[tip[1]], z=[tip[2]],
            u=[E_dir[0]], v=[E_dir[1]], w=[E_dir[2]],
            sizemode="absolute", sizeref=L*0.12,
            colorscale=[[0, "#FF8C00"], [1, "#FF4500"]],
            showscale=False,
            anchor="tip",
            hoverinfo="skip",
            showlegend=False,
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title="x [m]", yaxis_title="y [m]", zaxis_title="z [m]",
            aspectmode="cube",
            xaxis=dict(range=[-L, L]),
            yaxis=dict(range=[-L, L]),
            zaxis=dict(range=[-L, L]),
            bgcolor="#0F1220",
        ),
        paper_bgcolor="#171B2C",
        font=dict(color="#ECEAE4"),
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=0.99,
                    xanchor="left", x=0.01,
                    bgcolor="rgba(23,27,44,0.8)"),
    )

    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

st.divider()
with st.expander("📖 사용법 · 물리 배경"):
    st.markdown(r"""
**사용법**
1. 왼쪽 사이드바 ①에서 원하는 위치에 점전하 배치 (전하량 + xyz 좌표)
2. ②에서 전기장을 알고 싶은 좌표 입력
3. 3D 화면: 연한 보라 화살표 = **전기장 분포**, 노란 다이아몬드 = **쿼리 지점**, 굵은 주황 화살표 = **그 지점의 E 벡터**
4. 오른쪽 패널: 정확한 수치 결과 (성분, 크기, 방향)

**물리 배경**
쿨롱 법칙 + 중첩 원리:
$$\vec{E}(\vec{r}) = \sum_i \frac{k_e\, q_i\, (\vec{r} - \vec{r}_i)}{\left(|\vec{r} - \vec{r}_i|^2 + \varepsilon^2\right)^{3/2}}$$

- $k_e = 8.99 \times 10^9\,\mathrm{N\cdot m^2/C^2}$
- $\varepsilon = 10^{-9}$ m (특이점 회피)

**프로젝트:** 대전과학고 2026 1학년 자율생성 탐구활동 · 팀 1102 이온유·1106 김인하·1110 손수민·1114 최지원 · [GitHub](https://github.com/43th68-ship-it/em-simulator-jaseng)
""")