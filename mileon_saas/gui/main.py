import logging
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import ttk

import httpx

from mileon_saas.config import settings
from mileon_saas.services.full_site_parser import FullSiteParser


class SaaSApp:
    def __init__(self, root: tk.Tk) -> None:
        logging.basicConfig(
            filename="gui.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
        self.root = root
        self.root.title("Car Market Monitor - Рабочий стол")
        self.root.geometry("1200x720")
        self._center_window()

        self.filters = {
            "brand": "",
            "min_roi": 0.0,
            "min_buy_score": 0.0,
            "min_risk": 0.0,
        }
        self.rows = []
        self.status_var = tk.StringVar(value="Готово")
        self.last_error = ""
        self.api_process = None
        self.api_log_handle = None
        self.sort_column = None  # Tracking sort state
        self.sort_reverse = False
        self.full_parser_running = False
        self.parser_start_time = 0
        self.parser_timer_id = None

        self._build_ui()
        self.reload_data()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _format_time(self, seconds: float) -> str:
        """Format elapsed seconds as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _build_ui(self) -> None:
        filter_frame = tk.LabelFrame(self.root, text="Фильтры")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Марка").grid(row=0, column=0, padx=5, pady=5)
        self.brand_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.brand_var, width=16).grid(row=0, column=1)

        tk.Label(filter_frame, text="ROI >=").grid(row=0, column=2, padx=5)
        self.roi_var = tk.StringVar(value="")
        tk.Entry(filter_frame, textvariable=self.roi_var, width=8).grid(row=0, column=3)

        tk.Label(filter_frame, text="Оценка покупки >=").grid(row=0, column=4, padx=5)
        self.buy_score_var = tk.StringVar(value="")
        tk.Entry(filter_frame, textvariable=self.buy_score_var, width=8).grid(row=0, column=5)

        tk.Label(filter_frame, text="Риск >=").grid(row=0, column=6, padx=5)
        self.risk_var = tk.StringVar(value="")
        tk.Entry(filter_frame, textvariable=self.risk_var, width=8).grid(row=0, column=7)

        tk.Button(filter_frame, text="Применить", command=self.apply_filters).grid(row=0, column=8, padx=10)
        tk.Button(filter_frame, text="Обновить", command=self.reload_data).grid(row=0, column=9, padx=5)

        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        tk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        tk.Button(status_frame, text="Копировать ошибку", command=self.copy_error).pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.parser_tab = tk.Frame(self.notebook)
        self.decisions_tab = tk.Frame(self.notebook)
        self.risks_tab = tk.Frame(self.notebook)

        self.notebook.add(self.parser_tab, text="Парсер")
        self.notebook.add(self.decisions_tab, text="Решения")
        self.notebook.add(self.risks_tab, text="Риски")

        self._build_parser_tab()
        self._build_decisions_tab()
        self._build_risks_tab()

    def _build_parser_tab(self) -> None:
        controls = tk.Frame(self.parser_tab)
        controls.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(controls, text="Запустить API", command=self.start_api).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Запустить парсер", command=self.run_parser).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Импортировать данные", command=self.ingest_data).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Обновить", command=self.reload_data).pack(side=tk.LEFT, padx=5)
        
        self.full_parse_btn = tk.Button(controls, text="Парсить весь сайт", command=self.full_site_parse)
        self.full_parse_btn.pack(side=tk.LEFT, padx=5)

        info = tk.Label(
            self.parser_tab,
            text="Запускает parser.py, импортирует cars_data.json и обновляет монитор.",
        )
        info.pack(anchor=tk.W, padx=10)
        
        full_parse_info = tk.Label(
            self.parser_tab,
            text="'Парсить весь сайт' - загружает все объявления myauto.ge (работает в фоне, с защитой от блокировок)",
            font=("Arial", 9),
            fg="blue"
        )
        full_parse_info.pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.count_label = tk.Label(self.parser_tab, text="Объявлений: 0")
        self.count_label.pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        # Progress bar for full site parser
        progress_frame = tk.Frame(self.parser_tab)
        progress_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.progress_label = tk.Label(progress_frame, text="")
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, mode='indeterminate', length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.parser_status_label = tk.Label(progress_frame, text="")
        self.parser_status_label.pack(anchor=tk.W, pady=(5, 0))

    def _build_decisions_tab(self) -> None:
        table_frame = tk.Frame(self.decisions_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = (
            "Оценка сделки",
            "Оценка покупки",
            "Ожид. продажа",
            "Чистая прибыль",
            "ROI",
            "Статус",
            "Марка",
            "Модель",
            "Год",
            "Цена",
        )

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor=tk.CENTER)

        self.tree.column("Марка", width=140, anchor=tk.W)
        self.tree.column("Модель", width=160, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-1>", self._on_column_header_click)
        self.decisions_empty_label = tk.Label(self.decisions_tab, text="Нет данных для отображения")
        self.decisions_empty_label.pack(anchor=tk.CENTER, pady=5)

    def _build_risks_tab(self) -> None:
        table_frame = tk.Frame(self.risks_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = (
            "Оценка риска",
            "Флаги риска",
            "Решение",
            "Марка",
            "Модель",
            "Год",
            "Цена",
            "ROI",
        )

        self.risk_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.risk_tree.heading(col, text=col)
            self.risk_tree.column(col, width=130, anchor=tk.CENTER)

        self.risk_tree.column("Флаги риска", width=260, anchor=tk.W)
        self.risk_tree.column("Марка", width=140, anchor=tk.W)
        self.risk_tree.column("Модель", width=160, anchor=tk.W)

        self.risk_tree.pack(fill=tk.BOTH, expand=True)
        self.risk_tree.bind("<Button-1>", self._on_column_header_click)
        self.risks_empty_label = tk.Label(self.risks_tab, text="Нет данных для отображения")
        self.risks_empty_label.pack(anchor=tk.CENTER, pady=5)

    def reload_data(self) -> None:
        try:
            self.rows = self._fetch_rows()
            total = len(self.rows)
            self.status_var.set(f"Загружено объявлений: {total}")
            if hasattr(self, "count_label"):
                self.count_label.config(text=f"Объявлений: {total}")
            if hasattr(self, "notebook"):
                self.notebook.select(self.decisions_tab)
            logging.info("Loaded %s listings", len(self.rows))
        except httpx.HTTPError as exc:
            self.last_error = str(exc)
            self.status_var.set(f"Ошибка API: {exc}")
            logging.exception("API error on reload")
            self.rows = []
        self.apply_filters()

    def _fetch_rows(self) -> list[dict]:
        url = f"{settings.api_base_url}/api/listings"
        params = {
            "company_id": settings.default_company_id,
            "with_scores": True,
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        rows = []
        for item in payload:
            rows.append({
                "listing": item["listing"],
                "scores": item["scores"],
            })

        return rows

    def run_parser(self) -> None:
        self.status_var.set("Запуск парсера...")
        logging.info("Starting parser")
        thread = threading.Thread(target=self._run_parser_thread, daemon=True)
        thread.start()

    def start_api(self) -> None:
        if self.api_process and self.api_process.poll() is None:
            self.status_var.set("API уже запущен")
            logging.info("API already running")
            return

        self.status_var.set("Запуск API...")
        logging.info("Starting API")
        thread = threading.Thread(target=self._start_api_thread, daemon=True)
        thread.start()

    def _start_api_thread(self) -> None:
        if self.api_log_handle:
            try:
                self.api_log_handle.close()
            except OSError:
                pass

        self.api_log_handle = open("api.log", "a", encoding="utf-8")
        self.api_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "mileon_saas.api.main:app",
                "--reload",
            ],
            stdout=self.api_log_handle,
            stderr=self.api_log_handle,
        )
        if self._wait_for_api():
            self.root.after(0, lambda: self.status_var.set("API запущен"))
            logging.info("API started successfully")
        else:
            self.root.after(0, lambda: self.status_var.set("API не запустился (см. api.log)"))
            logging.error("API failed to start")

    def _wait_for_api(self, timeout_seconds: int = 15) -> bool:
        deadline = time.time() + timeout_seconds
        url = f"{settings.api_base_url}/health"
        while time.time() < deadline:
            try:
                response = httpx.get(url, timeout=3.0)
                if response.status_code == 200:
                    return True
            except httpx.HTTPError:
                logging.warning("API not ready yet")
                time.sleep(1.0)
        return False

    def _run_parser_thread(self) -> None:
        result = subprocess.run(
            [sys.executable, "parser.py"],
            capture_output=False,
        )
        if result.returncode != 0:
            self.root.after(0, lambda: self.status_var.set("Парсер завершился с ошибкой"))
            logging.error("Parser failed with code %s", result.returncode)
            return

        try:
            self._ingest_via_api()
            self.root.after(0, self.reload_data)
        except httpx.HTTPError as exc:
            message = str(exc)
            self.last_error = message
            self.root.after(0, lambda: self.status_var.set(f"Ошибка импорта: {message}"))
            logging.exception("Ingest failed after parser")

    def ingest_data(self) -> None:
        self.status_var.set("Импорт данных...")
        logging.info("Starting ingest")
        thread = threading.Thread(target=self._ingest_thread, daemon=True)
        thread.start()

    def _ingest_thread(self) -> None:
        try:
            self._ingest_via_api()
            self.root.after(0, self.reload_data)
        except httpx.HTTPError as exc:
            message = str(exc)
            self.last_error = message
            self.root.after(0, lambda: self.status_var.set(f"Ошибка импорта: {message}"))
            logging.exception("Ingest failed")

    def _ingest_via_api(self) -> None:
        if not self._wait_for_api():
            logging.error("API unavailable for ingest")
            raise httpx.ConnectError("API недоступен", request=None)
        url = f"{settings.api_base_url}/api/listings/ingest"
        params = {
            "path": "cars_data.json",
            "company_id": settings.default_company_id,
        }
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, params=params)
            response.raise_for_status()

    def copy_error(self) -> None:
        if not self.last_error:
            self.status_var.set("Нет ошибки для копирования")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_error)
        self.status_var.set("Ошибка скопирована")

    def apply_filters(self) -> None:
        self.filters["brand"] = self.brand_var.get().strip().lower()
        self.filters["min_roi"] = None
        if self.roi_var.get().strip():
            try:
                self.filters["min_roi"] = float(self.roi_var.get())
            except ValueError:
                self.filters["min_roi"] = None

        self.filters["min_buy_score"] = None
        if self.buy_score_var.get().strip():
            try:
                self.filters["min_buy_score"] = float(self.buy_score_var.get())
            except ValueError:
                self.filters["min_buy_score"] = None

        self.filters["min_risk"] = None
        if self.risk_var.get().strip():
            try:
                self.filters["min_risk"] = float(self.risk_var.get())
            except ValueError:
                self.filters["min_risk"] = None

        filtered = []
        for row in self.rows:
            listing = row["listing"]
            scores = row["scores"]

            brand_value = (listing.get("brand") or "").lower()
            if self.filters["brand"] and self.filters["brand"] not in brand_value:
                continue
            if self.filters["min_roi"] is not None and scores["roi_percent"] < self.filters["min_roi"]:
                continue
            if self.filters["min_buy_score"] is not None and scores["buy_score"] < self.filters["min_buy_score"]:
                continue
            if self.filters["min_risk"] is not None and scores["risk_score"] < self.filters["min_risk"]:
                continue

            filtered.append(row)

        self.status_var.set(f"Показано: {len(filtered)} / {len(self.rows)}")
        self._render_table(filtered)

    def full_site_parse(self) -> None:
        """Start full site parsing in background thread."""
        if self.full_parser_running:
            self.status_var.set("Парсинг уже запущен")
            return
        
        self.full_parser_running = True
        self.full_parse_btn.config(state=tk.DISABLED)
        self.parser_start_time = time.time()
        
        thread = threading.Thread(target=self._full_parse_thread, daemon=True)
        thread.start()
        
        # Start timer for progress updates
        self._update_parser_timer()

    def _full_parse_thread(self) -> None:
        """Thread function for parsing full site."""
        try:
            def progress_cb(count: int, elapsed: float):
                """Callback for progress updates."""
                self.root.after(0, lambda: self._update_parser_ui(count, elapsed))
            
            parser = FullSiteParser(delay_seconds=2.0, progress_callback=progress_cb)
            
            # Load existing data to enable deduplication
            parser._load_existing_data()
            existing_count = len(parser.existing_car_ids)
            print(f"Loaded {existing_count} existing car IDs - duplicates will be skipped")
            
            # Parse all pages with deduplication enabled
            parser.parse_all_pages(max_pages=None, skip_existing=True)
            
            # Save to file
            output_file = parser.save_to_file()
            
            elapsed = time.time() - self.parser_start_time
            
            # Calculate skipped count
            skipped_count = existing_count  # Simplified - actual count tracked in parser
            
            self.root.after(0, lambda: self._finish_parsing(
                parser.new_listings_count, 
                output_file, 
                elapsed,
                total_checked=len(parser.all_listings) + skipped_count,
                skipped=skipped_count
            ))
        except Exception as e:
            self.last_error = str(e)
            self.root.after(0, lambda: self._finish_parsing_error(str(e)))

    def _update_parser_ui(self, count: int, elapsed: float) -> None:
        """Update progress bar UI."""
        elapsed_str = self._format_time(elapsed)
        self.progress_label.config(text=f"Загружено: {count} объявлений | Время: {elapsed_str}")
        
        # Animate progress bar
        if not self.progress_bar.winfo_exists():
            return
        
        if self.progress_bar['value'] == 100:
            self.progress_bar['value'] = 0
        else:
            self.progress_bar['value'] += 1

    def _update_parser_timer(self) -> None:
        """Update elapsed time display."""
        if not self.full_parser_running:
            return
        
        elapsed = time.time() - self.parser_start_time
        elapsed_str = self._format_time(elapsed)
        
        # Update status if no callback has updated recently
        if not self.progress_label.cget("text"):
            self.progress_label.config(text=f"Парсинг... | Время: {elapsed_str}")
        
        self.parser_timer_id = self.root.after(1000, self._update_parser_timer)

    def _finish_parsing(self, total_items: int, output_file: str, elapsed: float, total_checked: int = 0, skipped: int = 0) -> None:
        """Handle successful parsing completion."""
        self.full_parser_running = False
        self.full_parse_btn.config(state=tk.NORMAL)
        self.progress_bar.stop()
        
        elapsed_str = self._format_time(elapsed)
        
        # Format message with deduplication info
        if skipped > 0:
            msg = f"✓ Парсинг завершен: {total_items} новых + {skipped} пропущено (дубли) | Время: {elapsed_str}"
            status_msg = f"Новых: {total_items} | Пропущено: {skipped} | Файл: {output_file}"
            status_summary = f"Парсинг завершен: {total_items} новых объявлений, {skipped} дубликатов пропущено"
        else:
            msg = f"✓ Парсинг завершен: {total_items} объявлений | Время: {elapsed_str}"
            status_msg = f"Сохранено в: {output_file}"
            status_summary = f"Парсинг завершен: {total_items} объявлений загружено"
        
        self.progress_label.config(text=msg)
        self.parser_status_label.config(text=status_msg)
        self.status_var.set(status_summary)
        logging.info(f"Full site parsing completed: {total_items} new items, {skipped} duplicates skipped in {elapsed_str}")

    def _finish_parsing_error(self, error_msg: str) -> None:
        """Handle parsing error."""
        self.full_parser_running = False
        self.full_parse_btn.config(state=tk.NORMAL)
        self.progress_bar.stop()
        
        self.progress_label.config(text="✗ Ошибка при парсинге")
        self.parser_status_label.config(text=error_msg, foreground="red")
        self.status_var.set("Ошибка парсинга")
        logging.exception("Full site parsing failed")

    def _sort_rows_by_column(self, rows: list[dict], column: str, reverse: bool = False) -> list[dict]:
        """Sort rows by column value."""
        sort_keys = {
            "Оценка сделки": lambda r: r["scores"]["deal_score"],
            "Оценка покупки": lambda r: r["scores"]["buy_score"],
            "Ожид. продажа": lambda r: r["scores"]["expected_sell_price"],
            "Чистая прибыль": lambda r: r["scores"]["net_profit"],
            "ROI": lambda r: r["scores"]["roi_percent"],
            "Статус": lambda r: r["scores"]["decision"],
            "Марка": lambda r: (r["listing"].get("brand") or "").lower(),
            "Модель": lambda r: (r["listing"].get("model") or "").lower(),
            "Год": lambda r: r["listing"].get("year") or 0,
            "Цена": lambda r: r["listing"].get("price_usd") or 0,
        }
        
        if column not in sort_keys:
            return rows
        
        return sorted(rows, key=sort_keys[column], reverse=reverse)

    def _on_tree_double_click(self, event) -> None:
        """Navigate to listing URL on double-click."""
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        tags = self.tree.item(item_id, "tags")
        if tags and len(tags) > 0:
            source_listing_id = tags[0]
            url = f"https://www.myauto.ge/ka/pr/{source_listing_id}"
            try:
                webbrowser.open(url)
                logging.info(f"Opened URL: {url}")
            except Exception as exc:
                self.last_error = str(exc)
                logging.exception("Failed to open browser")

    def _on_column_header_click(self, event) -> None:
        """Sort table by column on header click."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "heading":
            return

        col = self.tree.identify_column(event.x)
        col_index = int(col[1:]) - 1
        
        columns = (
            "Оценка сделки",
            "Оценка покупки",
            "Ожид. продажа",
            "Чистая прибыль",
            "ROI",
            "Статус",
            "Марка",
            "Модель",
            "Год",
            "Цена",
        )
        
        if col_index < 0 or col_index >= len(columns):
            return

        column_name = columns[col_index]
        
        # Toggle sort direction if same column clicked
        if self.sort_column == column_name:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_name
            self.sort_reverse = False
        
        self.apply_filters()

    def _render_table(self, rows: list[dict]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.risk_tree.get_children():
            self.risk_tree.delete(item)

        if hasattr(self, "decisions_empty_label"):
            if rows:
                self.decisions_empty_label.pack_forget()
            else:
                self.decisions_empty_label.pack(anchor=tk.CENTER, pady=5)

        if hasattr(self, "risks_empty_label"):
            if rows:
                self.risks_empty_label.pack_forget()
            else:
                self.risks_empty_label.pack(anchor=tk.CENTER, pady=5)

        # Apply sorting if column is selected
        sorted_rows = rows
        if self.sort_column:
            sorted_rows = self._sort_rows_by_column(rows, self.sort_column, self.sort_reverse)

        for row in sorted_rows:
            listing = row["listing"]
            scores = row["scores"]
            source_listing_id = listing.get("source_listing_id", "")
            self.tree.insert(
                "",
                "end",
                values=(
                    f"{scores['deal_score']:.1f}",
                    f"{scores['buy_score']:.1f}",
                    f"${scores['expected_sell_price']:.0f}",
                    f"${scores['net_profit']:.0f}",
                    f"{scores['roi_percent']:.1f}%",
                    scores["decision"],
                    listing.get("brand", ""),
                    listing.get("model", ""),
                    listing.get("year") or "",
                    f"${listing['price_usd']:.0f}" if listing.get("price_usd") else "",
                ),
                tags=(source_listing_id,),
            )

            self.risk_tree.insert(
                "",
                "end",
                values=(
                    f"{scores['risk_score']:.1f}",
                    ", ".join(scores.get("risk_flags", [])),
                    scores["decision"],
                    listing.get("brand", ""),
                    listing.get("model", ""),
                    listing.get("year") or "",
                    f"${listing['price_usd']:.0f}" if listing.get("price_usd") else "",
                    f"{scores['roi_percent']:.1f}%",
                ),
            )


def main() -> None:
    root = tk.Tk()
    app = SaaSApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
