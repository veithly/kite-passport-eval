# Kite Proofroom / Passport Skills 评测运行器

这是本周贡献方向 **Passport Skills Eval Runner** 的完整项目，作者 Rick / GitHub `@veithly`。项目使用 AI 辅助开发，不是 Kite 官方产品。

[在线报告](https://veithly.github.io/kite-passport-eval/) · [回归门禁](https://veithly.github.io/kite-passport-eval/regression-gate/) · [CI 工作流](.github/workflows/ci.yml) · [英文完整说明](README.md) · [验收映射](docs/ACCEPTANCE.md)

## 交付内容

保留官方 `evals.json` 的全部 **138 个用例、424 条断言**，使用可替换模型适配器执行；每条断言输出通过/失败、匹配行号和字符位置。报告支持离线 HTML、JSON、Markdown、JUnit XML、哈希清单，并有搜索、技能筛选、状态筛选和原始响应查看。

当前已完成 **41 项自动测试**及 **424 个逐条删除变异**；已知过期命令和 case 31 的字面断言盲区均有可重复的回归测试。GitHub Actions 不依赖钱包、模型密钥或付费请求。

## 真实结果，不刷通过率

真实调用使用 Claude CLI 2.1.202，返回模型名 `claude-haiku-4-5`。首轮 138 个用例全部执行，其中一个调用错误；只对这个错误做了一次独立补测，并保留原始失败报告。

恢复后 **138/138 有有效响应，81 个用例字面通过、57 个字面失败，321/424 条断言命中**。没有把失败改成通过，也没有重试已经评分的用例来挑选更高分答案。调用均为无工具文本模式，没有执行登录、支付、钱包转账或卖家部署。

运行器测试通过与模型用例通过是两件事：CI 的绿色意味着评分、错误处理和重放正确，不意味着模型表现全通过。字面命中也不能证明步骤顺序、语义正确或链上执行。真实响应的语义审查仍标记为待审；项目另提供与响应哈希绑定的人工审查接口。

## 第 2 周新增：回归门禁

1.1 版本新增 `kite-eval compare`。它可以把新的完整评测报告与已知基线逐条比较：只要出现“原本通过的字面断言消失”、case 状态变差、或语义审查状态降级，CI 就以退出码 `1` 失败。即使同一个 case 同时有其他断言改善，也不会抵消已经发生的退步。

```bash
python3 -m kite_eval compare \
  --baseline evidence/recovered/report.json \
  --candidate runs/replay-01/report.json \
  --out runs/regression-gate
```

比较器拒绝不同 suite hash、case 集、断言列表以及自相矛盾的 report 状态；不信任来源报告里的 summary，而是重新推导计数。输出离线 HTML、JSON、Markdown、JUnit XML 与 SHA-256 清单，并明确记录响应哈希是否变化。GitHub Actions 已把该门禁加入 Linux / macOS 验证矩阵。详细规则见 [REGRESSION_GATE.md](docs/REGRESSION_GATE.md)。

## 复现

需要 Python 3.9+ 与 Git。命令从本仓库根目录执行：

```bash
git clone https://github.com/gokite-ai/passport-skills.git vendor/passport-skills
git -C vendor/passport-skills checkout 1ff773981566ac1755ccf23e98983cd76c81bf08
python3 scripts/verify.py --upstream vendor/passport-skills --out runs/verify-01 --require-live
```

查看 `runs/verify-01/verification.json` 与 `live-replay/index.html`。每次使用新的输出目录，旧证据不会被覆盖。完整安装、模型适配器、退出码和安全限制见英文 README。

全部工程与交付文件位于用户指定的 `Kite/passport-eval` 目录；上游参考源码位于相邻 `Kite/upstream/passport-skills`。活动验收、Electric Capital 仓库登记及奖励由活动方决定，本项目不承诺第三方审批结果。
