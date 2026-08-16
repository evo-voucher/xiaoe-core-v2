# XiaoE Core v2 Provenance

This repository is the independent XiaoE AI Core repository.

## Historical source
Earlier XiaoE architecture documents were temporarily stored inside:
`evo-voucher/evolution-optical-voucher`

Key historical evidence:
- Memory architecture v2.1 baseline commit: `9b2504606b81854756e15444fb2f3be28a521463`
- Voucher reconstruction alignment commit: `ac5c9221348075f8b0e85767138a2eed86413f13`

These historical records are evidence only. The active XiaoE source of truth is now this repository: `evo-voucher/xiaoe-core-v2`.

## Separation rule
XiaoE AI Core and Evolution Voucher are separate systems.

- XiaoE repo owns identity, behavior, memory contracts, runtime protocols, AI Router architecture, and AI-core documentation.
- Evolution Voucher repo owns Voucher application code and deployment artifacts.
- They must not share secrets, service-role credentials, or transactional database ownership.
- Future integration should use explicit APIs rather than shared database coupling.

## Migration policy
When migrating historical XiaoE material:
1. preserve important architecture meaning
2. remove display-only or obsolete implementation noise
3. keep the historical commit reference
4. do not copy Voucher business code into XiaoE Core
5. do not copy secrets or credentials
