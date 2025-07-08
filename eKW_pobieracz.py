from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import asyncio
import base64
import argparse
import logging


class EkwDownloader:
    def __init__(self, save_path=".", pdf_bg=False, ch1o=True, ch1s=False, ch2=True, ch3=False, ch4=False, chError=True):
        self.save_path = save_path
        self.pdf_bg = pdf_bg
        self.ch1o = ch1o
        self.ch1s = ch1s
        self.ch2 = ch2
        self.ch3 = ch3
        self.ch4 = ch4
        self.chError = chError
        self.consecutive_errors = 0
        self.rep_dict = {"X": "10", "A": "11", "B": "12", "C": "13", "D": "14", "E": "15",
                         "F": "16", "G": "17", "H": "18", "I": "19", "J": "20", "K": "21",
                         "L": "22", "M": "23", "N": "24", "O": "25", "P": "26", "R": "27",
                         "S": "28", "T": "29", "U": "30", "W": "31", "Y": "32", "Z": "33",
                         "0":"0", "1":"1", "2":"2", "3":"3", "4":"4", "5":"5", "6":"6", "7":"7", "8":"8", "9":"9"}

    def correct_kw_number(self, sad, number):
        sad_value = [self.rep_dict[s] for s in sad]
        wei = [1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7]
        while len(number) < 8:
            number = f"0{number}"
        j_value = [x for x in number]
        temp_kw = sad_value + j_value
        ctlr_dig = 0
        for k in range(len(wei)):
            ctlr_dig = ctlr_dig + (wei[k] * int(temp_kw[k]))
        ctlr_dig = ctlr_dig % 10
        skw = sad + "/" + number + f"/{ctlr_dig}"
        return skw

    async def save_kw_to_pdf_turbo(self, value: str):
        zupelna = False
        logging.info(f"Księga o numerze: {value}")
        try:
            kw = value.split('/')
            if 2 <= len(kw) < 3:
                value = self.correct_kw_number(kw[0], kw[1])
                kw = value.split('/')
                logging.info(f"Poprawiono cyfrę kontrolną: {value}")

            options = webdriver.ChromeOptions()
            browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            browser.get('https://przegladarka-ekw.ms.gov.pl/eukw_prz/KsiegiWieczyste/wyszukiwanieKW')
            await asyncio.sleep(3)

            elem = browser.find_element(By.ID, 'kodWydzialuInput')
            elem.send_keys(kw[0])
            elem = browser.find_element(By.NAME, 'numerKw')
            elem.send_keys(kw[1])
            elem = browser.find_element(By.NAME, 'cyfraKontrolna')
            elem.send_keys(kw[2])
            elem = browser.find_element(By.NAME, 'wyszukaj')
            elem.send_keys(Keys.RETURN)
            await asyncio.sleep(1)
            self.consecutive_errors = 0
            elem = browser.find_element(By.NAME, 'przyciskWydrukZwykly')
            elem.send_keys(Keys.RETURN)
        except (NoSuchElementException, TimeoutException) as e:
            zupelna = True
            logging.warning(f"Treść zwykła wydruku niedostępna dla: {value}. Powód: {e}")
        except WebDriverException as e:
            if "net::ERR_NAME_NOT_RESOLVED" in e.msg:
                self.consecutive_errors += 1
                logging.error(f"Błąd: {e.msg}")
                if self.consecutive_errors >= 3:
                    logging.error("Wystąpiły 3 kolejne błędy typu 'net::ERR_NAME_NOT_RESOLVED'. Serwis niedostępny, zamykam program.")
                    exit()
            else:
                self.consecutive_errors = 0
                logging.error(f"Nieoczekiwany błąd WebDriver: {e}")
            return
        except Exception as e:
            logging.error(f"Nieoczekiwany błąd podczas otwierania księgi {value}: {e}")
            return

        try:
            if zupelna:
                if self.chError:
                    elem = browser.find_element(By.NAME, 'przyciskWydrukZupelny')
                    elem.send_keys(Keys.RETURN)
                    logging.info("Pobieranie treści zupełnej")
                else:
                    logging.error(f"Błąd pobierania treści zupełnej księgi: {value}")
                    return
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Nie znaleziono przycisku do pobrania treści zupełnej dla {value}: {e}")
            return
        except Exception as e:
            logging.error(f"Nieoczekiwany błąd podczas pobierania księgi {value}: {e}")
            return

        try:
            if self.ch1o:
                await self.download_section(browser, "Dział I-O", value, "1o")
            if self.ch1s:
                await self.download_section(browser, "Dział I-Sp", value, "1s")
            if self.ch2:
                await self.download_section(browser, "Dział II", value, "2")
            if self.ch3:
                await self.download_section(browser, "Dział III", value, "3")
            if self.ch4:
                await self.download_section(browser, "Dział IV", value, "4")
            logging.info(f"Pobrano księgę: {value}")
        except (NoSuchElementException, TimeoutException) as e:
            logging.error(f"Błąd pobierania wybranych działów księgi {value}: {e}")
        except Exception as e:
            logging.error(f"Nieoczekiwany błąd podczas pobierania działów księgi {value}: {e}")

    async def download_section(self, browser, section_name, value, suffix):
        await asyncio.sleep(2)
        elem = browser.find_element(By.CSS_SELECTOR, f'[value="{section_name}"]')
        elem.send_keys(Keys.RETURN)
        pdf = browser.execute_cdp_cmd("Page.printToPDF", {"printBackground": self.pdf_bg})
        pdf_data = base64.b64decode(pdf["data"])
        with open(f"{self.save_path}/{value.replace('/', '.')}_{suffix}.pdf", "wb") as f:
            f.write(pdf_data)


async def run_by_list_turbo(downloader, kw_list_path, n):
    try:
        with open(kw_list_path, 'r') as file:
            values = file.readlines()
        distinct = sorted(set(values))
    except FileNotFoundError:
        logging.error(f"Plik wejściowy z listą kw nie został znaleziony: {kw_list_path}")
        return
    except Exception as e:
        logging.error(f"Błąd odczytu pliku: {e}")
        return

    task = []
    i = 0
    j = 0
    k = 0

    for value in distinct:
        if "/" not in value:
            continue
        value = value.replace("\n", "")
        task.append(asyncio.create_task(downloader.save_kw_to_pdf_turbo(value)))
        j += 1
        i += 1
        if j == n or i == len(distinct):
            k += 1
            logging.info(f"Pętla: {k}")
            await asyncio.gather(*task)
            task.clear()
            j = 0
    logging.info("Wszystkie księgi wieczyste z zadania zostały pobrane")


def main():
    parser = argparse.ArgumentParser(description="eKW pobieracz - terminal version")
    parser.add_argument("kw_list_path", help="Path to the file with a list of KW numbers")
    parser.add_argument("--save_path", default=".", help="Path to save PDF files")
    parser.add_argument("--n", type=int, default=5, help="Number of concurrent tasks")
    parser.add_argument("--all", action="store_true", help="Download all sections")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    if args.all:
        downloader = EkwDownloader(save_path=args.save_path, ch1o=True, ch1s=True, ch2=True, ch3=True, ch4=True, chError=True)
    else:
        downloader = EkwDownloader(save_path=args.save_path)
    asyncio.run(run_by_list_turbo(downloader, args.kw_list_path, args.n))


if __name__ == "__main__":
    main()
