from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parse_confluence_table(html: str, base_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    
    table = soup.find("table", class_="confluenceTable")
    if not table:
        raise ValueError("Таблица не найдена на странице")
    
    rows = table.find_all("tr")[1:]
    results = []

    for row in rows:
        cells = row.find_all("td")
        if not cells or len(cells) < 5:
            continue

        number = cells[0].get_text(strip=True)
        department = cells[1].get_text(strip=True)
        question = cells[2].get_text(strip=True)
        topic = cells[3].get_text(strip=True)
        last_cell = cells[4]

        file_urls = []
        for a in last_cell.find_all("a", class_="confluence-embedded-file"):
            href = a.get("href", "")
            if href:
                file_urls.append(urljoin(base_url, href))

        external_urls = []
        for a in last_cell.find_all("a", class_="external-link"):
            href = a.get("href", "")
            if href:
                external_urls.append(href)

        for a in last_cell.find_all("a"):
            href = a.get("href", "")
            if href and "download/attachments" in href and href not in file_urls:
                file_urls.append(urljoin(base_url, href))

        answer_text = ""
        if not file_urls and not external_urls:
            answer_text = last_cell.get_text(strip=True)

        results.append({
            "number": number,
            "department": department,
            "question": question,
            "topic": topic,
            "answer_text": answer_text,
            "file_urls": file_urls,
            "external_urls": external_urls,
        })

    return results


HTML = """

"""

if __name__ == "__main__":
    base_url = "https://confluence.glb.akron-holding.ru"
    results = parse_confluence_table(html=HTML, base_url=base_url)

    print(f"Спарсено строк: {len(results)}\n")
    for row in results:
        print(f"№{row['number']} | {row['department']}")
        print(f"Вопрос: {row['question'][:80]}")
        if row['file_urls']:
            print(f"Файлы: {len(row['file_urls'])}")
            for url in row['file_urls']: print(f"  -> {url}")
        if row['external_urls']:
            for url in row['external_urls']: print(f"  -> {url}")
        if row['answer_text']:
            print(f"Ответ: {row['answer_text'][:80]}")
        print("-"*50)