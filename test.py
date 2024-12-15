res = {
    'Sección A': {
        'Tipo 1': {'cantidad': 5, 'tiempo': 120},
        'Tipo 2': {'cantidad': 3, 'tiempo': 60},
    },
    'Sección B': {
        'Tipo 1': {'cantidad': 2, 'tiempo': 30},
    },
}

val = res.pop('Sección A')
res['Sección A'] = val
print(res)
print(val)