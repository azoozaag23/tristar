from frappe import _


def get_data():
    return [
        {
            "module_name": "TriStar Manufacturing",
            "color": "#1a6fbf",
            "icon": "octicon octicon-beaker",
            "type": "module",
            "label": _("TriStar Manufacturing"),
        },
        {
            "module_name": "TriStar Sales",
            "color": "#2ecc71",
            "icon": "octicon octicon-tag",
            "type": "module",
            "label": _("TriStar Sales"),
        },
        {
            "module_name": "TriStar HR",
            "color": "#e67e22",
            "icon": "octicon octicon-person",
            "type": "module",
            "label": _("TriStar HR"),
        },
        {
            "module_name": "TriStar Reports",
            "color": "#9b59b6",
            "icon": "octicon octicon-graph",
            "type": "module",
            "label": _("TriStar Reports"),
        },
    ]
