
import pandas as pd
import glob
import sys
import os

def card_value(card_str):
    if pd.isna(card_str):
        return None
    s = str(card_str).strip()
    if s.startswith('10'):
        return 0
    rank = s[0]
    if rank in ('T', 'J', 'Q', 'K'):
        return 0
    elif rank == 'A':
        return 1
    else:
        return int(rank)

def analyze_file(filepath):
    try:
        df = pd.read_excel(filepath, sheet_name='原始數據')
    except:
        return None
    results = []
    for _, row in df.iterrows():
        c1, c2, c3, c4 = card_value(row['卡片1']), card_value(row['卡片2']), card_value(row['卡片3']), card_value(row['卡片4'])
        c5, c6 = card_value(row['卡片5']), card_value(row['卡片6'])
        result = row['結果']
        if any(v is None for v in [c1, c2, c3, c4]):
            continue
        pi = (c1 + c3) % 10  # 閒初始點數
        bi = (c2 + c4) % 10  # 莊初始點數
        if pi >= 8 or bi >= 8:  # 排除天牌
            continue
        if result == '和':  # 排除和局
            continue
        if c5 is None:  # 必須有補牌
            continue

        pf, bf = pi, bi
        p3, b3 = None, None
        if pi <= 5:
            p3 = c5
            pf = (pi + c5) % 10
            if c6 is not None:
                b3 = c6
                bf = (bi + c6) % 10
        else:
            b3 = c5
            bf = (bi + c5) % 10

        if pi != 7 and bi != 7:
            continue

        who7 = '閒' if pi == 7 else '莊'
        rev = (who7 == '閒' and result == '莊') or (who7 == '莊' and result == '閒')
        results.append({
            '局號': row['局號'], '7點方': who7, '逆轉': rev,
            '閒初': pi, '莊初': bi, '閒補': p3, '莊補': b3,
            '閒終': pf, '莊終': bf, '結果': result,
        })
    return results

def main():
    # 預設讀取當前資料夾的 *.xlsx，也可指定路徑
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    files = sorted(glob.glob(os.path.join(folder, '*.xlsx')))

    if not files:
        print(f"在 {folder} 找不到 xlsx 檔案")
        return

    print(f"共 {len(files)} 個檔案\n")
    all_results = []

    for f in files:
        fname = os.path.basename(f).replace('.xlsx', '')
        res = analyze_file(f)
        if res is None:
            print(f"{fname}: ❌ 讀取失敗")
            continue

        total = len(res)
        rev = sum(1 for r in res if r['逆轉'])
        p7 = [r for r in res if r['7點方'] == '閒']
        b7 = [r for r in res if r['7點方'] == '莊']
        p7r = sum(1 for r in p7 if r['逆轉'])
        b7r = sum(1 for r in b7 if r['逆轉'])
        rate = f"{rev / total * 100:.1f}%" if total > 0 else "N/A"

        print(f"{'=' * 55}")
        print(f"📦 {fname}  |  7點局:{total}  逆轉:{rev}  逆轉率:{rate}")
        p7s = f"閒7: {p7r}/{len(p7)}" if p7 else "閒7: —"
        b7s = f"莊7: {b7r}/{len(b7)}" if b7 else "莊7: —"
        print(f"   {p7s}   {b7s}")
        print(f"{'─' * 55}")
        for r in res:
            mark = "⚠️逆轉" if r['逆轉'] else "  守住"
            p3 = f"+{r['閒補']}" if r['閒補'] is not None else "  "
            b3 = f"+{r['莊補']}" if r['莊補'] is not None else "  "
            print(f"  局{r['局號']:>3} | {r['7點方']}7 | 閒:{r['閒初']}{p3}→{r['閒終']}  莊:{r['莊初']}{b3}→{r['莊終']} | {r['結果']}贏 | {mark}")
        print()
        all_results.extend(res)

    # 總計
    print(f"{'=' * 55}")
    total_all = len(all_results)
    rev_all = sum(1 for r in all_results if r['逆轉'])
    p7a = [r for r in all_results if r['7點方'] == '閒']
    b7a = [r for r in all_results if r['7點方'] == '莊']
    p7ra = sum(1 for r in p7a if r['逆轉'])
    b7ra = sum(1 for r in b7a if r['逆轉'])
    print(f"🔥 全部合計 {len(files)} 副牌靴")
    print(f"   符合條件總局數: {total_all}")
    print(f"   被逆轉總局數:   {rev_all}")
    if total_all > 0:
        print(f"   整體逆轉機率:   {rev_all}/{total_all} = {rev_all / total_all * 100:.1f}%")
    if p7a:
        print(f"   閒家7點被逆轉:  {p7ra}/{len(p7a)} = {p7ra / len(p7a) * 100:.1f}%")
    if b7a:
        print(f"   莊家7點被逆轉:  {b7ra}/{len(b7a)} = {b7ra / len(b7a) * 100:.1f}%")
    if total_all > 0:
        avg_per_shoe = total_all / len(files)
        avg_rev_per_shoe = rev_all / len(files)
        print(f"\n   每副牌靴平均 {avg_per_shoe:.1f} 次7點局，{avg_rev_per_shoe:.1f} 次被逆轉")

if __name__ == '__main__':
    main()
