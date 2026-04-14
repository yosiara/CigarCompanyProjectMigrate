res = {
    'M-1': {
        'Subconjunto 1': {
            'Interrupcion 1': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 2': {'cantidad': 3, 'tiempo': 60},
        },
        '-': {
            'Interrupcion 6': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 7': {'cantidad': 3, 'tiempo': 60},
        },
        'Subconjunto 2': {
            'Interrupcion 3': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 4': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 5': {'cantidad': 10, 'tiempo': 80},
        },

    },
    'M-2': {
        '-': {
            'Interrupcion 9': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 10': {'cantidad': 3, 'tiempo': 60},
        },
        'Subconjunto 3': {
            'Interrupcion 1': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 2': {'cantidad': 3, 'tiempo': 60},
        },
    },
}

for _, v in res.items():
    if '-' in v:
        val = v['-']
        del v['-']
        v['-'] = val

print(res)
