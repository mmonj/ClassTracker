from typing import NamedTuple


class TPaginationData(NamedTuple):
    current_page: int  # current page number
    total_pages: int  # total number of pages
    has_previous: bool  # whether there's a previous page
    has_next: bool  # whether there's a next page
    previous_page_number: int  # previous page number (or None)
    next_page_number: int  # next page number (or None)
