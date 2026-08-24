# em-simulator-jaseng

대전과학고등학교 1학년 자율생성 탐구활동 (2026)
전자기장-입자 상호작용 시뮬레이션 및 응용 탐구

## 팀
- 1102 이온유 (팀장)
- 1106 김인하
- 1110 손수민
- 1114 최지원

## 단위 정책
- 기본은 SI 단위 (m, s, kg, C, T, V/m).
- 전자·양성자 스케일에서는 natural units (eV, ns, μm)로 무차원화 후 계산.

## 실행
```bash
uv sync
uv run jupyter lab
```

## 구조
- `src/fields/` — E, B, 합성 필드
- `src/particles/` — 하전입자 표현
- `src/integrators/` — RK4, Boris pusher
- `src/viz/` — 시각화 헬퍼
- `notebooks/` — 차시별 실험 노트북
- `tests/` — 해석해 vs 수치해 자동 비교
- `reports/` — 차시 요약 · 최종 보고서