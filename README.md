# Claude-for-Vertex-ai
使用官方SDK实现的将标准Anthropic Claude请求转发至VertexAI Claude的代理服务器应用，使用Fastapi。
支持Claude 3.5 sonnet, Claude 3 Opus/Sonnet/Haiku on Vertex AI

## 这个项目是做什么的？
这个项目在本地架设Fastapi服务器，将发送至此服务器的标准Anthropic请求处理模型名后使用官方Anthropic SDK将请求转发至Vertex AI Claude。

### Usage
#### 准备工作：
1.一个已启用结算账号或存在可用额度的GCP账号，且已启用Vertex AI API。（本步骤不提供教程）  
2.一个GCP VertexAI服务账号。  
3.一台可访问对应地区GCP资源的主机。  
4.Docker&Docker Compose或Python运行环境。（基于你的安装方式及系统）


#### 开始使用

##### 1. 必要前置条件：为GCP账号启用Vertex AI User用于验证：

<details>
  <summary>点击展开</summary>

**为避免不必要的安全性问题，本应用强烈建议使用服务账号限制应用和服务器对GCP的访问。**

1.点击GCP左上角Google图标，点击左上角导航栏，导航至IAM管理-服务账号
![F $O }NYM{J`{C0{90L){2J](https://github.com/TheValkyrja/Anthropic2Vertex/assets/45366459/e6a57671-dad8-4b7a-9dfd-20d62d7a35a3)  

2.创建服务账号  
![)E 7@C_U2{90I2VJUKM}FD](https://github.com/TheValkyrja/Anthropic2Vertex/assets/45366459/469d8314-cdc8-4d48-9299-9505d1fde7eb)

3.随意填写名字和ID，创建，搜索并为其选择Vertex AI User角色,完成创建。
![7(E GI8MUJNT `K CZTN15](https://github.com/TheValkyrja/Anthropic2Vertex/assets/45366459/c179b76d-7e04-4e43-90f2-bd789287bfcc)
![VR33I92N0Z0AANG 0T~)EGW](https://github.com/TheValkyrja/Anthropic2Vertex/assets/45366459/a561ce41-9aaa-417b-9d39-1312875e35fd)

4.点击右侧管理密钥。
![$ _7K@S1CN`O DYLC6HS$X](https://github.com/TheValkyrja/Anthropic2Vertex/assets/45366459/f38c9436-466a-42fe-b69b-fb80c1aabd46)

5.添加密钥-创建密钥-创建。
![` 8}9{$AO~Q5S1P$G3 PU4X](https://github.com/TheValkyrja/Anthropic2Vertex/assets/45366459/572b3e46-47ac-4201-a320-1fbfeacc3e93)

6.浏览器将会自动下载一个密钥文件，你不需要编辑它，只需要妥善保存。

**请像保护密码一样妥善保管此文件！！**

一旦遗失，无法重新下载，泄露将产生严重安全问题。
</details>

##### 2.下载、解压文件。  
**For Windows:**  
下载整个项目的压缩包或gitclone此项目地址到本地，并解压文件。

##### 3.配置文件。  
  1. 导航至解压的文件夹。
  2. 使用文本编辑器编辑.env文件：
     将端口，监听地址修改为你需要的服务器监听地址（默认127.0.0.1:5000）。
     并依照需求设置密码（为空即不认证，慎选）、访问地区、切换key的对话轮数等参数。
     访问区域填写为为你有权访问、且Claude on Vertex正常服务的地区，留空不填和示例已填入参数均为us-east5，根据需求自行修改。
     切换key的对话轮数即字面意思。
  3. 将前面下载的json文件命名为gcp-key0.json，放入项目根目录中，如有多个密钥则依次命名为gcp-key1.json、gcp-key2.json……以此类推。

##### 4.安装并启动
<details>
  
  <summary>从Docker部署启动(不推荐，本项目传到我这已经是三改项目了，docker配置文件过于古老，需要docker部署建议循着fork树找原项目去)</summary>
  
  本方法的优点：  
  1. 跨平台兼容性强  
  2. 环境隔离  
  3. 避免管理依赖，操作便捷  

  本方法的缺点：
  1. 需要docker环境  
  2. docker框架与镜像总占用空间偏大。

不包括docker框架，本应用镜像文件约占47.2MB（于Ubuntu22.04上本地构建）。

1. 根据你的平台安装对应docker和docker compose

2. 导航至文件夹

3. 启动应用
   运行
   ```
   docker compose up -d
   ```
   启动应用。

   这一指令会在后台将服务运行于你前面设置的地址和端口（默认127.0.0.1:5000）
   以酒馆为例，若你的服务与酒馆运行于同一主机，选择Claude聊天补全，并在代理服务器填入http://127.0.0.1:5000/v1  
   并将密码设置为你配置中的密码并测试连接。

   根据不同前端面板和应用需求设置各异，请自行调整。

安装完成，开始使用。

修改配置后，使用
```
docker compose down
docker compose up -d
```
重新加载配置。

4. （可选）删除目录下main与main.exe文件进一步节省空间。  
   注：照做这步后将无法使用二进制文件启动。确保你知道你在做什么，否则请无视。

</details>

<details>
  
  <summary>直接运行可执行文件（初次启动会下载嵌入式python等依赖）</summary>

1. 导航至文件目录。  
2. window用户双击start.bat（linux用户自行寻思寻思）
3. 等依赖装完就完事了，网络尽量保持通畅
   （注：linux用户怎么跑起来请自行寻思寻思）
</details>
