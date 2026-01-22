from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

"""
작동 원리
1. context - AI 환각(Hallucination)를 막기 위해 강제 주입
2. LLM - Upstage Solar 모델 사용
3. Process
    3-1. 사용자가 질문
    3-2. AI에게 명령 - "context를 읽고 사용자의 질문에 대해 네가 아는 문장력으로 자연스럽게 요약해서 답해"
    3-3. AI는 context에 있는 핵심 단어를 찾아 말을 생성하여 답변
-> ICL(In-context Learning, 문맥 학습)
"""

app = FastAPI()

# 1. 참고사항: 건설 안전 데이터 (DB 대신 하드코딩)
SAFETY_CONTEXT = """
[삼성물산 건설 안전 수칙 요약]
1. 높이 2m 이상 작업 시 반드시 안전대를 착용하고 고리를 체결해야 한다.
2. 밀폐 공간 작업 시 작업 전 산소 및 유해가스 농도를 측정해야 한다.
3. 굴착 작업 시 붕괴 방지를 위해 흙막이 지보공을 설치해야 한다.
4. 이동식 크레인 사용 시 아웃트리거를 필수로 설치하고 지반 지지력을 확인한다.
5. 화기 작업 시 소화기를 비치하고 화재 감시자를 배치해야 한다.
"""

# 2. OpenAI 모델 설정
llm = ChatUpstage(
    api_key='up_',
    model_name="solar-pro2"
)

# 3. 프롬프트 템플릿 (건설 전문가 페르소나 부여)
template = """
당신은 삼성물산 건설 현장의 안전관리 AI 어시스턴트입니다.
아래의 [안전 수칙]을 바탕으로 질문에 대해 친절하고 전문적으로 답변하세요.
수칙에 없는 내용은 "관련 규정을 확인 후 다시 답변 드리겠습니다."라고 하세요.

[안전수칙]
{context}

질문: {question}
답변:"""

prompt = PromptTemplate.from_template(template)

# 4. 체인 생성 (질문 -> 프롬프트 -> LLM -> 문자열 출력)
chain = (
    {"context": lambda x: SAFETY_CONTEXT, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

class QuestionRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_safety_rule(request: QuestionRequest):
    try:
        response = chain.invoke(request.query)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 실행 명령: uvicorn main:app --reload --port 8000