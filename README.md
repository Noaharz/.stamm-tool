---

# What is a `.stamm` file?

* `.stamm` is a **custom file format for family trees**.
* It is basically a **ZIP archive** that contains:

  1. **`.dfile` files** — one for each person, storing personal info (name, birth, gender, notes).
  2. **`relationships.json`** — describing who is related to whom (parents, children, spouse).

### `.dfile` format

Each `.dfile` stores **one person’s profile**:

```
!=! (start)
NAME: Max Mustermann
GEBURT: 1975-03-15
STERBEDATUM: 
GENDER: M
GEBURTSORT: Berlin
VERSION: 1
NOTIZ: Family patriarch
FOTO: 
!0! (end)
```

* **NAME** = Full name
* **GEBURT** = Birth date
* **STERBEDATUM** = Death date (optional)
* **GENDER** = M or F
* **GEBURTSORT** = Place of birth
* **VERSION** = File version
* **NOTIZ** = Notes
* **FOTO** = Optional photo path

---

### `relationships.json` format

Stores **connections between people**:

```json
{
  "max.dfile": {
      "spouse": "anna.dfile",
      "children": ["lukas.dfile","sophie.dfile"]
  },
  "anna.dfile": {
      "spouse": "max.dfile",
      "children": ["lukas.dfile","sophie.dfile"]
  },
  "lukas.dfile": {
      "parents": ["max.dfile","anna.dfile"]
  },
  "sophie.dfile": {
      "parents": ["max.dfile","anna.dfile"]
  }
}
```

* **parents** = list of parents
* **children** = list of children (optional)
* **spouse** = partner (optional)

> Any person with no family can have empty `{ "parents": [] }`.

---

### How `.stamm` works

* Think of `.stamm` as a **container for a family tree**:

  ```
  .stamm = ZIP(.dfile + relationships.json)
  ```
* You can open it in the **Stamm Viewer**, which will read all `.dfile`s and `relationships.json`, then draw the **family tree** with:

  * Parent → child lines (black)
  * Spouse lines (red)
  * Male/female color coding
  * Clickable boxes to view `.dfile` info

---

### Summary

* `.stamm` = ZIP archive of **profiles + relationships**
* `.dfile` = single person profile
* `relationships.json` = family connections
* Viewer reads `.stamm` and shows a **visual family tree**

---
