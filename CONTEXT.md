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
