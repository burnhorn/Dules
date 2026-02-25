# ==========================================
# Stage 1: Builder (의존성 설치용 환경)
# ==========================================
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# 컴파일에 필요한 OS 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ==========================================
# Stage 2: Runtime (실제 실행되는 가벼운 환경)
# ==========================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Seoul

WORKDIR /app

# 런타임에 필요한 최소한의 라이브러리만 설치 (gcc 제외)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Builder 스테이지에서 빌드된 wheel 파일들을 가져와서 시스템에 설치
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# 소스 코드 복사
COPY . .

# 보안 강화를 위한 non-root 유저 생성 및 권한 부여
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser