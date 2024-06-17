from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import openai
import asyncio

app = FastAPI()

class KakaoRequest(BaseModel):
    userRequest: dict

# OpenAI API 키 설정
openai.api_key = 'Open Ai API Key'

async def generate_image_and_send(callback_url, prompt):
    # 이미지 생성
    response = await openai.Image.acreate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )

    # 생성된 이미지 URL 추출
    image_url = response['data'][0]['url']
    template = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleImage": {
                        "imageUrl": image_url,
                        "altText": "요청한 그림"
                    }
                }
            ]
        }
    }

    # 비동기적으로 POST 요청 보내기
    async with httpx.AsyncClient() as client:
        await client.post(callback_url, json=template)

@app.post('/image')
async def image(request: KakaoRequest):
    prompt = request.userRequest['utterance']
    callback_url = request.userRequest['callbackUrl']

    # 비동기적으로 이미지 생성 및 POST 요청을 보내도록 예약
    asyncio.create_task(generate_image_and_send(callback_url, prompt))

    # 즉시 응답 반환
    return {
        "version": "2.0",
        "useCallback": True,
        "data": {
            "text": "생각하고 있는 중이에요😘 \n15초 정도 소요될 거 같아요 기다려 주실래요?!" # 기다리는동한 카톡 챗봇이 보여줄 메세지
        }
    }

# 애플리케이션 실행 (이 코드는 uvicorn을 사용하여 애플리케이션을 실행할 때 사용합니다)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
