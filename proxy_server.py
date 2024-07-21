import json
import tempfile
import os
import sys
import platform
import globalVar
from typing import Optional, Union

import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
from anthropic import AnthropicVertex
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from secrets import compare_digest

# 获取临时目录路径
if platform.system() == 'Windows':
    temp_dir = tempfile.gettempdir()
else:
    temp_dir = '/dev/shm'

temp_key_path = os.path.join(temp_dir, 'temp_auth.json')

jsondata = globalVar.accountdata
accountIndex = 0
accountName = ""
region = globalVar.region
switch_frequency = globalVar.switch_frequency
messageCount = 0

# 初始化 FastAPI 应用程序
app = FastAPI()

# 获取环境变量 DOCKER_ENV，如果没有设置，默认为 False
is_docker = os.environ.get('DOCKER_ENV', 'False').lower() == 'true'

#加载文件目录
def get_base_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 如果是从Python运行
        return os.path.dirname(os.path.abspath(__file__))
    
initial_index = int(os.getenv('GCP_KEY_INDEX', '0'))
jsondata, key_file_names = globalVar.accountdata, globalVar.key_file_names
accountIndex = initial_index  # 使用从 .env 文件读取的索引初始化 accountIndex
accountName = ""
temp_key_path = os.path.join('/dev/shm', 'temp_auth.json')
hostaddr = '0.0.0.0' if is_docker else os.environ.get('host', '127.0.0.1')

if len(os.environ.get('host', '127.0.0.1')) == 0:
    hostaddr = '127.0.0.1'

if len(os.environ.get('port', '5000')) == 0:
    lsnport = int(5000)
else:
    lsnport = int(os.environ.get('port', 5000))

if len(os.environ.get('counter', '0')) == 0:
    timeToSwotch = int(0)
else:
    timeToSwotch = int(os.environ.get('counter', 0))

password = os.environ.get('password')
messageCount = 0

# VertexAI 配置
vertex_client = None

def changeActiveAccount(index=None):
    global accountIndex, accountName, vertex_client
    
    if index is None:
        # 如果没有指定索引，切换到下一个账号
        accountIndex = (accountIndex + 1) % len(jsondata)
    else:
        # 如果指定了索引，使用指定的索引
        accountIndex = index % len(jsondata)
    
    os.makedirs(os.path.dirname(temp_key_path), exist_ok=True)
    with open(temp_key_path, 'w') as f:
        json.dump(jsondata[accountIndex], f)
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_key_path
    
    accountName = jsondata[accountIndex]['project_id']
    vertex_client = AnthropicVertex(project_id=accountName, region=region)
    vertexai.init(project=accountName, location=region)
    print(f"\033[32mINFO\033[0m:     当前登录\"{accountName}\". Key文件:{key_file_names[accountIndex]}, 地区:{region}")

# 使用从 .env 文件读取的初始索引初始化第一个账号
changeActiveAccount(initial_index)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    model: str
    stream: Optional[bool] = False
    # 添加其他可能的字段

def vertex_model(original_model):
    # 定义模型名称映射
    mapping_file = os.path.join(get_base_path(), 'model_mapping.json')
    with open(mapping_file, 'r') as f:
        model_mapping = json.load(f)
    return model_mapping[original_model]

# 比较密码
def check_auth(api_key: Optional[str]) -> bool:
    if not password:  # 如果密码未设置或为空字符串
        return True
    return api_key and compare_digest(api_key, password)

@app.get("/")
async def ping():
    Main = 'Anthropic2Vertex修改版 by zxcPandora'
    index_msg = "<!DOCTYPE html>\\n<html>\\n<head>\\n<meta charset=\"utf-8\">\\n<script>\\nfunction copyToClipboard(text) {\\n  var textarea = document.createElement(\"textarea\");\\n  textarea.textContent = text;\\n  textarea.style.position = \"fixed\";\\n  document.body.appendChild(textarea);\\n  textarea.select();\\n  try {\\n    return document.execCommand(\"copy\");\\n  } catch (ex) {\\n    console.warn(\"Copy to clipboard failed.\", ex);\\n    return false;\\n  } finally {\\n    document.body.removeChild(textarea);\\n  }\\n}\\nfunction copyLink(event) {\\n  event.preventDefault();\\n  const url = new URL(window.location.href);\\n  const link = url.protocol + '//' + url.host + '/v1';\\n  copyToClipboard(link);\\n  alert('链接已复制: ' + link);\\n}\\n</script>\\n</head>\\n<body>\\n" + Main + "<br/><br/>完全开源、免费且禁止商用<br/><br/>点击复制反向代理: <a href=\"v1\" onclick=\"copyLink(event)\">Copy Link</a><br/>复制后填入 代理服务器 URL 中并选择你在Vertex中的已启用的claude模型（Claude API Key中随便填点什么，但不能为空）<br/><br/>教程与FAQ: <a href=\"https://rentry.org/zxcPandora_cloud_proxy\" target=\"FAQ\">Rentry</a> | <a href=\"https://github.com/TheValkyrja/Anthropic2Vertex\" target=\"FAQ\">Anthropic2Vertex原作者仓库</a><br/><br/><br/>❗警惕任何高风险cookie/伪api(25k cookie)购买服务，以及破坏中文AI开源共享环境倒卖免费资源抹去署名的群组（🈲黑名单：酒馆小二、AI新服务、浅睡(鲑鱼)、赛博女友制作人(青麈/overloaded/科普晓百生)🈲）\\n</body>\\n</html>"
    return HTMLResponse(content = index_msg.replace("\\n", "\n").replace("\\", '').replace('\\"', '"'))

def translateResponseToSillytavernFormat(text,usage_metadata):
    responseData = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": text
                }],
                "role": "model"
            },
            "finishReason": "STOP",
            "index": 0
        }],
        "usageMetadata": {
            "promptTokenCount": usage_metadata.prompt_token_count,
            "candidatesTokenCount": usage_metadata.candidates_token_count,
            "totalTokenCount": usage_metadata.total_token_count
        }
    }
    return responseData

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE
}

@app.post("/v1beta/models/{requestModel}")
async def gemini_proxy(request: Request, requestModel: str ,key: str,alt:Union[str,None] = None):
    # 密码验证
    if not check_auth(key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    if timeToSwotch != 0:
        global messageCount
        messageCount += 1
        if messageCount == timeToSwotch:
            changeActiveAccount(accountIndex+1)
            messageCount = 0
        
    data = await request.json()

    sendModel = requestModel.split(":")[0].replace("-latest", "-001")
    stream = alt or requestModel.split(":")[1] == "streamGenerateContent"
    contents = data.get('contents')
    generationConfig =  data.get('generationConfig')
    system_instruction = data.get('system_instruction')['parts']['text'] if data.get('system_instruction') else None

    gemini_config = {}
    for key, value in generationConfig.items():
        if key == 'stopSequences':
            if any(not seq for seq in value):
                value = [seq for seq in value if seq]
            gemini_config["stop_sequences"] = value
        elif key == 'candidateCount':
            gemini_config["candidate_count"] = value
        elif key == 'maxOutputTokens':
            gemini_config["max_output_tokens"] = value
        elif key == 'topP':
            gemini_config["top_p"] = value
        elif key == 'topK':
            gemini_config["top_k"] = value
        elif key == 'responseMimeType':
            gemini_config["response_mime_type"] = value
        elif key == 'responseSchema':
            gemini_config["response_schema"] = value
        else:
            gemini_config[key] = value

    aiModel = GenerativeModel(model_name=sendModel, system_instruction=system_instruction)
    print(f"\033[32mINFO\033[0m:     Request Model: \"{sendModel}\"")

    try: 
        if stream:
            def generate():
                for chunk in aiModel.generate_content(json.dumps(contents), generation_config=gemini_config, safety_settings=safety_settings, stream=True):
                    response = f"data: {json.dumps(translateResponseToSillytavernFormat(chunk.text,chunk.usage_metadata))}\n\n"
                    yield response
            
            return StreamingResponse(generate(),
                 media_type='text/event-stream',
                 headers={'X-Accel-Buffering': 'no'})
        else:
            response = aiModel.generate_content(json.dumps(contents), generation_config=gemini_config, safety_settings=safety_settings, stream=False)
            return JSONResponse(content=translateResponseToSillytavernFormat(response.text,response.usage_metadata), status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/v1/messages")
async def proxy_request(request: Request, x_api_key: Optional[str] = Header(None)):
    global messageCount
    
    # 密码验证
    if not check_auth(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 检查是否需要切换账号
    if switch_frequency > 0:
        messageCount += 1
        if messageCount >= switch_frequency:
            changeActiveAccount()  # 切换到下一个账号
            messageCount = 0  # 重置计数器
    
    data = await request.json()

    try:
        vertex_request = {}

        for key, value in data.items():
            if key == 'model':
                vertex_request[key] = vertex_model(value)
                print(f"\033[32mINFO\033[0m:     Request Model: \"{vertex_model(value)}\"")
            else:
                vertex_request[key] = value

        if vertex_request.get('stream', False):
            def generate():
                yield 'event: ping\ndata: {"type": "ping"}\n\n'
                for chunk in vertex_client.messages.create(**vertex_request):
                    response = f"event: {chunk.type}\ndata: {json.dumps(chunk.model_dump())}\n\n"
                    yield response

            return StreamingResponse(generate(),
                                     media_type='text/event-stream',
                                     headers={'X-Accel-Buffering': 'no'})
        else:
            response = vertex_client.messages.create(**vertex_request)
            return JSONResponse(content=response.model_dump(), status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=hostaddr, port=lsnport)
