# Chani AI Trading

Binance 현물 + 선물 자동매매 시스템

## 스택
- **백엔드**: Python 3.12 / FastAPI / ccxt / SQLite
- **프론트엔드**: React / Tailwind CSS / Recharts
- **알림**: Telegram
- **인프라**: Docker Compose

## 시작하기

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 2. 실행
docker compose up -d

# 대시보드: http://localhost:3000
# API 문서: http://localhost:8000/docs
```

## 필요한 API 키 (.env)

| 키 | 설명 |
|----|------|
| `BINANCE_API_KEY` | Binance API Key |
| `BINANCE_SECRET_KEY` | Binance Secret Key |
| `TELEGRAM_BOT_TOKEN` | @BotFather 에서 발급 |
| `TELEGRAM_CHAT_ID` | @userinfobot 에서 확인 |

## 전략

### RSI 역추세 (`rsi_reversal`) - 현물
- RSI < 30 → 매수
- RSI > 70 → 매도
- 주요 파라미터: `timeframe`, `rsi_period`, `oversold`, `overbought`, `risk_pct`

### 볼린저밴드 + RSI (`bb_rsi`) - 선물
- 2σ 돌파 + RSI 과매도/과매수 → 신규 진입
- 4σ 돌파 + RSI 극값 → 추가 진입
- BB 중심선 복귀 or RSI 중립 → 청산
- 주요 파라미터: `timeframe`, `bb_period`, `bb_std1(2)`, `bb_std2(4)`, `leverage`, `risk_pct`

## 프로젝트 구조

```
├── backend/
│   ├── core/
│   │   ├── exchanges/      # 거래소 모듈
│   │   ├── strategies/     # rsi_reversal.py, bb_rsi.py
│   │   └── notifications/  # telegram.py
│   ├── api/routes/         # REST API
│   ├── database/           # SQLite 모델
│   └── main.py
├── frontend/               # React 대시보드
└── docker-compose.yml
```
