# Module Deep Dive Template

Use this template when the user asks to understand a specific model, layer, algorithm block, or target file.

## 1. 论文公式与代码的映射

- State the core formula or algorithm in concise terms.
- Locate the exact file/class/function.
- Explain the smallest necessary code snippet line by line.
- Say whether the implementation exactly matches the paper or is an engineering approximation.

## 2. 张量形状追踪

Use explicit shape notation.

```text
input_name [BatchSize, SeqLen, EmbedDim]
  -> operator/function
  -> output_name [BatchSize, NewDim]
```

Always call out shape-changing operations:

- `squeeze` / `unsqueeze`
- `transpose` / `permute`
- `reshape` / `view`
- `cat` / `stack`
- masking and padding
- broadcasting
- packed sequence utilities

## 3. 核心 API 与算子解析

Pick 1-3 core framework APIs and explain why they matter.

Examples:

- `torch.matmul` / `torch.bmm`: batched vector or matrix scoring.
- `torch.einsum`: compact high-order feature crossing.
- `nn.Embedding`: sparse ID to dense vector lookup.
- `pack_padded_sequence`: avoid wasted GRU computation on padding.
- `F.softmax`: normalize attention/gating weights.

Mention why vectorized operators are preferred over Python loops for GPU utilization and memory locality.

## 4. 踩坑与魔改建议

Cover:

- OOM risks: long sequences, large vocabularies, high-order crosses, large batch size.
- Numerical issues: sigmoid saturation, masking values, empty sequence lengths.
- Cold-start features and unknown IDs.
- Where to modify safely if changing attention, pooling, tower structure, loss, or output head.
- What tests or shape assertions to run after modification.
