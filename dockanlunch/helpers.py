from calendar import TimeEncoding, day_name

def get_day_name(day_no, locale = "sv_SE", lower = True):
    with TimeEncoding(locale) as encoding:
        s = day_name[day_no]
        if encoding is not None:
            s = s.decode(encoding)
        if lower:
            s = s.lower()
        return s

