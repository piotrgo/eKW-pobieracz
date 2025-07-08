# eKW-pobieracz (wersja CLI)

Proste narzędzie wiersza poleceń (CLI) do masowego pobierania ksiąg wieczystych z serwisu Ministerstwa Sprawiedliwości (ekw.ms.gov.pl).

## Instalacja

1.  Sklonuj repozytorium:
    ```bash
    git clone https://github.com/piotrgo/eKW-pobieracz.git
    cd eKW-pobieracz
    ```

2.  (Opcjonalnie, ale zalecane) Utwórz i aktywuj środowisko wirtualne:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Na Windows użyj: .venv\Scripts\activate
    ```

3.  Zainstaluj wymagane zależności:
    ```bash
    pip install -r requirements.txt
    ```

## Sposób użycia

Program uruchamia się z wiersza poleceń, podając ścieżkę do pliku z listą numerów ksiąg wieczystych.

### Składnia

```bash
python eKW_pobieracz.py <ścieżka_do_pliku_z_listą> [opcje]
```

### Argumenty

*   `kw_list_path`: (wymagany) Ścieżka do pliku tekstowego zawierającego listę numerów KW do pobrania.
*   `--save_path`: (opcjonalny) Ścieżka do folderu, w którym zostaną zapisane pliki PDF. Domyślnie jest to bieżący folder (`.`).
*   `--n`: (opcjonalny) Liczba jednoczesnych zadań (wątków) pobierania. Domyślnie `5`.
*   `--all`: (opcjonalny) Pobiera wszystkie dostępne działy księgi wieczystej. Domyślnie pobierane są tylko działy I-O, II i III.

### Format pliku wejściowego

Plik wejściowy (`kw_list_path`) powinien być plikiem tekstowym, w którym każdy numer księgi wieczystej znajduje się w nowej linii.

Format numeru KW: `AA1A/NNNNNNNN/K`
*   `AA1A` - kod wydziału sądu
*   `NNNNNNNN` - numer księgi
*   `K` - cyfra kontrolna (jeśli jej brakuje, program obliczy ją automatycznie)

**Przykład pliku `lista_kw.txt`:**
```
KR1P/00123456/7
WA1M/00098765/4
GD1G/00011122/0
```

### Przykłady użycia

1.  Pobieranie ksiąg z pliku `lista_kw.txt` z domyślnymi ustawieniami:
    ```bash
    python eKW_pobieracz.py lista_kw.txt
    ```

2.  Pobieranie ksiąg i zapisywanie ich w folderze `/Users/nazwa/Dokumenty/KW` z 10 jednoczesnymi zadaniami:
    ```bash
    python eKW_pobieracz.py lista_kw.txt --save_path /Users/nazwa/Dokumenty/KW --n 10
    ```

3.  Pobieranie wszystkich działów dla każdej księgi:
    ```bash
    python eKW_pobieracz.py lista_kw.txt --all
    ```

## Format plików wyjściowych

Pobrane działy ksiąg wieczystych są zapisywane jako osobne pliki PDF w formacie:
`AA1A.NNNNNNNN.K_dział.pdf`

Na przykład: `KR1P.00123456.7_1o.pdf`, `KR1P.00123456.7_2.pdf`, itd.