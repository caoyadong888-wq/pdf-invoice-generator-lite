# PDF Invoice Generator (Lite)

## English

JSON to PDF for a seller, a buyer, and line items. The total is the sum of quantity times unit price. There is no tax line.

This subset has no YAML, no tax percent, no notes, and no due date.

### Deliverables

- `deliverables/make_invoice_lite.py` — JSON invoice writer
- `deliverables/invoice.lite.json` — one patch-cable line, total 30.00
- `examples/sample-invoice.json` — two lines, total 152.50

### Quick start

```bash
python3 deliverables/make_invoice_lite.py \
  --input examples/sample-invoice.json \
  --output /tmp/invoice-lite.pdf
```

Exit 0 when the PDF is written. Exit 2 when the JSON is invalid. Sample mailboxes are `billing@example.com` and `accounts@example.com`.

## 中文

这是从 JSON 生成 PDF 的精简工具。内容有卖方、买方和明细。合计是数量乘单价之和。没有税额行。

精简版没有 YAML、没有税率百分比、没有备注，也没有到期日。

### 交付文件

- `deliverables/make_invoice_lite.py` — JSON 发票写入
- `deliverables/invoice.lite.json` — 一行跳线，合计 30.00
- `examples/sample-invoice.json` — 两行明细，合计 152.50

### 快速开始

```bash
python3 deliverables/make_invoice_lite.py \
  --input examples/sample-invoice.json \
  --output /tmp/invoice-lite.pdf
```

写出 PDF 时退出码为 0，JSON 无效时为 2。示例邮箱是 `billing@example.com` 和 `accounts@example.com`。

Full version: GUMROAD_URL
