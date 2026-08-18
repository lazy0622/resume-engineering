# PDF 渲染与校验参考

这份参考只在用户要求生成 PDF、出现分页/乱码/路径问题，或需要排查 RenderCV
版本时读取。内容源仍然是 YAML，PDF/PNG/HTML/Typst 都是派生文件。

## 推荐运行时

优先使用已经安装 RenderCV 2.8 的 bundled Python：

```powershell
$python = 'C:\Users\29215\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -c "import rendercv; print(rendercv.__version__)"
```

项目旧虚拟环境可能是 RenderCV 2.2。2.2 的字段模型与当前母版中
`design.typography`、`design.page.show_top_note`、`locale.language` 等字段不兼容，
不要为了让旧版本通过而删改母版字段。

## 快速生成

```powershell
$script = 'C:\Users\29215\.codex\skills\resume-engineering\scripts\render_resume.py'
& $python -X utf8 $script $yaml `
  --output-dir 'C:\Users\29215\Documents\项目一\output\pdf' `
  --stem '汪岱原_简历母版_带照片'
```

默认行为：

- 从 YAML 所在目录解析照片、主题和相对资源；
- 在隐藏 staging 目录生成，避免把上一次的 PDF 当成这一次的结果；
- 只发布一个 PDF 和一个 PNG（多页时为 `stem_1.png`、`stem_2.png`）；
- 验证 PDF `%PDF-` 文件签名，并默认要求一页；
- 2.2 走 Python API，跳过无超时的 PyPI 版本检查；2.8 走 CLI，命令最长 180 秒；
- 失败时保留最终输出目录，但不会留下 staging 临时目录。

需要 Markdown、HTML 和 Typst 中间文件时：

```powershell
& $python -X utf8 $script $yaml `
  --output-dir 'C:\Users\29215\Documents\项目一\output\resume-master\rendered' `
  --stem 'resume' --all
```

只有确认简历确实允许多页时，才使用 `--allow-multi-page`；投递版默认不要使用。

## 交付前快速检查

```powershell
$pdf = 'C:\Users\29215\Documents\项目一\output\pdf\汪岱原_简历母版_带照片.pdf'
Format-Hex -Path $pdf -Count 5
Get-Item -LiteralPath $pdf | Select-Object FullName,Length,LastWriteTime
```

然后打开同 stem 的 PNG，检查：

1. 只有一页 A4，页底没有截断；
2. 中文、英文技术名和数字没有乱码或异常换行；
3. 照片比例、日期列和项目标题正常；
4. 没有“最后更新于”、旧岗位标题或“定向版”文件名；
5. PDF 的修改时间与本次生成时间一致。

## 排障顺序

1. 先看生成命令使用的 Python 和 `rendercv.__version__`；
2. 再看 YAML 是否 UTF-8、是否混入旧 schema 字段；
3. 再看 PNG 是否两页、页底是否截断；
4. 最后才调整字号、边距和项目条数；
5. 不直接编辑 Typst/PDF 来“修”内容，修复必须回到 YAML。
