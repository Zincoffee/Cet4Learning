<p align="center">
  <a href="https://turborepo.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/4060187/196936123-f6e1db90-784d-4174-b774-92502b718836.png">
      <img src="https://user-images.githubusercontent.com/4060187/196936104-5797972c-ab10-4834-bd61-0d1e5f442c9c.png" height="128">
    </picture>
    <h1 align="center">Turborepo</h1>
  </a>
</p>

<p align="center">
  <a aria-label="Vercel logo" href="https://vercel.com/"><img src="https://img.shields.io/badge/MADE%20BY%20Vercel-000000.svg?style=for-the-badge&logo=Vercel&labelColor=000"></a>
  <a aria-label="NPM version" href="https://www.npmjs.com/package/turbo"><img alt="" src="https://img.shields.io/npm/v/turbo.svg?style=for-the-badge&labelColor=000000"></a>
  <a aria-label="License" href="https://github.com/vercel/turborepo/blob/main/LICENSE"><img alt="" src="https://img.shields.io/npm/l/turbo.svg?style=for-the-badge&labelColor=000000&color="></a>
  <a aria-label="Join the community on GitHub" href="https://github.com/vercel/turborepo/discussions"><img alt="" src="https://img.shields.io/badge/Join%20the%20community-blueviolet.svg?style=for-the-badge&logo=turborepo&labelColor=000000&logoWidth=20&logoColor=white"></a>
</p>

## 概述

Turborepo 是面向编码代理（coding agent）的构建系统。

## 仓库结构

仓库根目录由 pnpm 工作区与 Cargo 工作区（Rust）组成：

```text
.
├── apps/                 # pnpm 工作区成员
├── crates/               # Cargo 工作区（Rust）中的 crate
├── docs/                 # pnpm 工作区成员
├── examples/             # pnpm 工作区成员，工作区排除 examples/non-monorepo
├── lockfile-tests/       # pnpm 工作区成员
├── packages/             # pnpm 工作区成员，工作区排除 packages/turbo
├── plans/
├── scripts/
├── skills/
├── test-codemod/
├── turborepo-tests/
├── .cargo/
├── .config/
├── .devcontainer/
├── .github/
├── .husky/
├── Cargo.toml            # Cargo 工作区清单
├── CONTRIBUTING.md       # 贡献指南
├── CODE_OF_CONDUCT.md    # 行为准则
├── LICENSE               # 许可证
├── README.md
├── SECURITY.md
├── package.json
├── pnpm-workspace.yaml   # pnpm 工作区成员定义
├── turbo.json
└── version.txt
```

## 快速开始

访问 https://turborepo.dev 开始使用 Turborepo。

该项目在 npm 上以 `turbo` 为包名发布，见 [npm 页面](https://www.npmjs.com/package/turbo)。

## 常用命令

依赖由 pnpm 安装，根 `package.json` 的 `packageManager` 字段为 `pnpm@12.0.0`：

```bash
pnpm install            # 安装依赖
pnpm run build:turbo    # 构建 turbo
pnpm run turbo          # 构建 turbo 后运行 ./target/debug/turbo
pnpm run rustdoc        # 生成 Rust 文档
```

## 贡献与社区

贡献方式见 [CONTRIBUTING.md](https://github.com/vercel/turborepo/blob/main/CONTRIBUTING.md)。

Turborepo 社区位于 [GitHub Discussions](https://github.com/vercel/turborepo/discussions)，可以在其中提问、提出想法并分享项目。

与其他社区成员交流，可加入 [Vercel Community 的 `#turborepo` 标签](https://vercel.community/tag/turborepo)。

[行为准则](https://github.com/vercel/turborepo/blob/main/CODE_OF_CONDUCT.md)适用于所有 Turborepo 社区渠道。

## 使用方

Turborepo 被多家国际领先企业使用，详见 [Turborepo Showcase](https://turborepo.dev/showcase)。

## 更新

项目更新见 X 上的 [@turborepo](https://x.com/turborepo)。

## 安全

如果认为发现了 Turborepo 的安全漏洞，建议负责任地披露，而不要提交公开 issue。所有合法报告都会得到调查。安全漏洞可发送邮件至 `security@vercel.com`。

https://security.vercel.com/

## 许可证

本项目的许可证见 [LICENSE](https://github.com/vercel/turborepo/blob/main/LICENSE)。
