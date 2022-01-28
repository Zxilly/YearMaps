# YearMaps

![PyPI](https://img.shields.io/pypi/v/yearmaps) ![Docker Image Version (latest by date)](https://img.shields.io/docker/v/zxilly/yearmaps)

生成一年的热力图。

![image](https://user-images.githubusercontent.com/31370133/150357084-f0ddb8f5-26c0-4526-9f3e-bc1e3aa1784a.png)

# 安装

```bash
pip[3] install --user yearmaps
```

# 使用

```bash
Usage: yearmaps [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --data-dir TEXT             Directory to store datas  [default: ~/.yearmaps]
  -o, --output-dir TEXT           Directory to store output  [default: $(pwd)]
  -f, --file-type [svg|png]       File type to export  [default: svg]
  -m, --mode [till_now|year]      Generate mode of the program  [default: till_now]
  -y, --year INTEGER              Year to generate, this option will override mode to "year"
  -c, --color [red|pink|purple|deeppurple|indigo|blue|lightblue|cyan|teal|green|lightgreen|lime|yellow|amber|orange|deeporange|brown|grey|bluegrey]
                                  Color to override provider default color
  --help                          Show this message and exit.

Commands:
  bbdc    不背单词
  bili    Bilibili
  cf      Codeforces
  github  GitHub
  
# 服务器模式

Usage: yearmaps-server [OPTIONS]

Options:
  -l, --host TEXT     Host to listen on.  [default: 0.0.0.0]
  -p, --port INTEGER  Port to listen on.  [default: 5000]
  -f, --config TEXT   Path to config file.  [default: $(pwd)/yearmaps.yml]
  --help              Show this message and exit.
```

## 子模块

### 不背单词

<details>

```bash
Usage: yearmaps bbdc [OPTIONS]

  不背单词

Options:
  -i, --id  TEXT          不背单词用户 ID  [required]
  -t, --type [time|word]  图数据类型
  --help                  Show this message and exit.
```

![bbdc](https://user-images.githubusercontent.com/31370133/150357416-36b3bd83-aa8c-4065-aabb-f130f0392476.png)

</details>

### bilibili

<details>
  
```bash
Usage: yearmaps bili [OPTIONS]

  bilibili

Options:
  -i, --id TEXT       bilibili uid  [required]
  -t, --type [video]  图数据类型
  --help              Show this message and exit.
```
  
![image](https://user-images.githubusercontent.com/50107074/150572220-781dd51f-fd9c-47cf-b78a-cac1def2fd91.png)
  
</details>

### Codeforces

<details>

```bash
Usage: yearmaps cf [OPTIONS]

  Codeforces

Options:
  -u, --user TEXT      Codeforces user name  [required]
  -t, --type [all|ac]  图数据类型
  --help               Show this message and exit.
```


![image](https://user-images.githubusercontent.com/31370133/150477193-6740583e-f3b8-48a3-b92c-f40b4af010b8.png)

</details>

### GitHub

<details>

```bash
Usage: yearmaps github [OPTIONS]

  GitHub

Options:
  -u, --user TEXT       GitHub user name  [required]
  -k, --token TEXT      GitHub access token  [required]
  -t, --type [contrib]  图数据类型
  --help                Show this message and exit.
```

![image](https://user-images.githubusercontent.com/31370133/150357084-f0ddb8f5-26c0-4526-9f3e-bc1e3aa1784a.png)

</details>
