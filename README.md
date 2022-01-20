# YearMaps

生成一年的热力图。

# 安装

```bash
pip[3] install --user yearmaps
```

# 使用

```bash
Usage: yearmaps [OPTIONS] COMMAND [ARGS]...

Options:
  -d, --data-dir TEXT         Directory to store datas  [default:
                              ~\.yearmaps]
  -o, --output-dir TEXT       Directory to store output  [default:
                              current directory]
  -m, --mode [till_now|year]  Generate mode of the program  [default:
                              till_now]
  -y, --year INTEGER          Year to generate, this options depends on
                              mode=year  [default: 2022]
  --help                      Show this message and exit.

Commands:
  bbdc    不背单词
  github  GitHub
```

## 子模块

### 不背单词

<details>

```bash
Usage: yearmaps bbdc [OPTIONS]

  不背单词

Options:
  -i, --id TEXT           不背单词用户 ID  [required]
  -t, --type [time|word]  图数据类型
  --help                  Show this message and exit.
```

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

</details>