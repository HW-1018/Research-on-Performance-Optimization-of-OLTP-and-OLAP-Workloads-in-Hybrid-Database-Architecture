# Research-on-Performance-Optimization-of-OLTP-and-OLAP-Workloads-in-Hybrid-Database-Architecture
## 1. 安裝與啟動 SingleStore (Docker )

### 1.1 安裝 Docker

確認系統是否已安裝 Docker，可以執行以下指令來檢查：

```bash
docker --version
docker-compose --version
```

若尚未安裝，請前往 [Docker 官網](https://www.docker.com/) 下載安裝包，並依照官方說明完成安裝。

---

### 1.2 下載 SingleStore Docker 映像檔

使用 Docker Hub 下載 SingleStore 的單節點部署映像檔：

```bash
docker pull memsql/cluster-in-a-box
```

> 📦 `memsql/cluster-in-a-box` 是 SingleStore 提供的**單節點部署**解決方案，適合開發與測試用途。

---

### 1.3 啟動 SingleStore 容器

執行以下指令以啟動 SingleStore 並對外映射相關埠口：

```bash
docker run -d \
  --name singlestore \
  -p 3306:3306 \     # MySQL 預設端口
  -p 8080:8080 \     # SingleStore 管理介面端口
  -e LICENSE_KEY=<YOUR_LICENSE_KEY> \ # License 金鑰 (必須)
  memsql/cluster-in-a-box
```

---

### 📌 參數說明

- `--name singlestore`：指定容器名稱為 `singlestore`
- `-p 3306:3306`：開放 MySQL 預設連接埠
- `-p 8080:8080`：開放 SingleStore 管理介面連接埠
- `-e LICENSE_KEY=<YOUR_LICENSE_KEY>`：填入你的 License 金鑰
- `memsql/cluster-in-a-box`：使用剛剛下載的映像檔來啟動容器

---

## 2. 專案結構

建議的專案目錄結構如下：
```bash
project/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt                
├── src                  #
  ├── initialize
  ├── operator
  └── turn_into_graph
└── README.md                  

```

