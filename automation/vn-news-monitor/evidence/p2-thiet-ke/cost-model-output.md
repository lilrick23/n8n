## Ket qua tinh (sinh tu scripts/cost_model.py)

### 1. Phan loai, theo kich ban va cach goi

| Kich ban | Tin/ngay | Mo hinh | Gom lo | Luot goi/ngay | Token vao/ngay | Token ra/ngay | USD/ngay | USD/thang (22 ngay) |
|---|---|---|---|---|---|---|---|---|
| thap | 30 | `claude-haiku-5-5` | 10 | 3 | 15,918 | 5,700 | 0.0044 | 0.0977 |
| thap | 30 | `claude-haiku-5-5` | 1 | 30 | 78,180 | 8,400 | 0.0120 | 0.2644 |
| thap | 30 | `claude-sonnet-5-5` | 10 | 3 | 15,918 | 5,700 | 0.0888 | 1.9544 |
| vua | 80 | `claude-haiku-5-5` | 10 | 8 | 42,448 | 15,200 | 0.0118 | 0.2606 |
| vua | 80 | `claude-haiku-5-5` | 1 | 80 | 208,480 | 22,400 | 0.0320 | 0.7051 |
| vua | 80 | `claude-sonnet-5-5` | 10 | 8 | 42,448 | 15,200 | 0.2369 | 5.2117 |
| cao | 200 | `claude-haiku-5-5` | 10 | 20 | 106,120 | 38,000 | 0.0296 | 0.6515 |
| cao | 200 | `claude-haiku-5-5` | 1 | 200 | 521,200 | 56,000 | 0.0801 | 1.7626 |
| cao | 200 | `claude-sonnet-5-5` | 10 | 20 | 106,120 | 38,000 | 0.5922 | 13.0293 |

### 2. Kiem tra do nhay: neu mo hinh van suy nghi (thinking) 1.000 token moi luot

| Kich ban | Mo hinh | Gom lo | USD/ngay khi tat thinking | USD/ngay khi co thinking | Chenh lech |
|---|---|---|---|---|---|
| thap | `claude-haiku-5-5` | 10 | 0.0044 | 0.0059 | x1.34 |
| vua | `claude-haiku-5-5` | 10 | 0.0118 | 0.0158 | x1.34 |
| cao | `claude-haiku-5-5` | 10 | 0.0296 | 0.0396 | x1.34 |

### 3. Ban tin tong hop (2 lan/ngay)

| Mo hinh | Token vao/ngay | Token ra/ngay | USD/ngay | USD/thang (22 ngay) |
|---|---|---|---|---|
| `claude-haiku-5-5` | 9,400 | 3,000 | 0.0024 | 0.0537 |
| `claude-sonnet-5-5` | 9,400 | 3,000 | 0.0488 | 1.0736 |
| `claude-opus-5-5` | 9,400 | 3,000 | 0.0976 | 2.1472 |

### 4. Tong theo cau hinh mac dinh (phan loai Haiku 5.5 gom 10 + ban tin Sonnet 5.5)

| Kich ban | USD/ngay | USD/thang (22 ngay) |
|---|---|---|
| thap | 0.0532 | 1.1713 |
| vua | 0.0606 | 1.3342 |
| cao | 0.0784 | 1.7251 |
