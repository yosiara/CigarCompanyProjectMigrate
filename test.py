res = {
    'Sección A': {
        'Subconjunto 1': {
            'Interrupcion 1': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 2': {'cantidad': 3, 'tiempo': 60},
        },
        'Subconjunto 2': {
            'Interrupcion 3': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 4': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 5': {'cantidad': 10, 'tiempo': 80},
        } 
    },
    'Sección B': {
        'Subconjunto 3': {
            'Interrupcion 1': {'cantidad': 3, 'tiempo': 60},
            'Interrupcion 2': {'cantidad': 3, 'tiempo': 60},
        },
    },
}

val = res.pop('Sección A')
res['Sección A'] = val
print(res)
print(val)