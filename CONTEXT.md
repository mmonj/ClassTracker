# ClassTracker

Tracks CUNY class availability by scraping the public class catalog, and alerts recipients when a watched section opens up.

## Language

**Globalsearch**:
CUNY Global Search (globalsearch.cuny.edu), the public class catalog site that this project scrapes all of its class and catalog data from.
_Avoid_: CUNYfirst, the catalog, GS

**Globalsearch Key**:
The identifier Globalsearch itself uses for a school, term, career or subject (eg. `QNS01` for a school, `1259` for a term). Outside this project the same value is often called a "code", as in "term code" or "school code".
_Avoid_: Slug, external id

**Class Number**:
The number Globalsearch assigns to a course section (eg. `43070`). It is only meaningful within a term and school; a different school may reuse the same number.
_Avoid_: Section number, section id, class id

**Variable-Topic Section**:
A course section whose topic differs from its course's title. The course title is a generic name (eg. "Special Topics in Computer Sci") and the section's topic is the specialization actually being taught (eg. "Cryptography").
_Avoid_: Special topics section, topic section

**Course Prefix**:
The short letters that start a course's name as a school writes it (eg. `CSCI` in "CSCI 316"). Each school chooses its own, so different schools may use different prefixes for the same **Subject** (eg. Queens College `CSCI` vs Baruch `CIS`, both under Globalsearch subject `CMSC`). It is not a **Globalsearch Key**.
_Avoid_: Course code, subject code
