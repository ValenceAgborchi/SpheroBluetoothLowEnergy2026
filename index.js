document.getElementById('connecttosphero').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/connect', {method:'POST'})
    const data = await result.json()
    document.getElementById('console').value += '\n Connected!'

})

document.getElementById('disconnectsphero').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/disconnect', {method: 'POST'})
    const data = await result.json()
    document.getElementById('console').value += '\n Disconnected'

})


document.getElementById('red').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/colour', {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({r: 255, g: 0, b: 0})

    })
    document.getElementById('console').value += '\n Colour changed to Red'
})

document.getElementById('green').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/colour', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({r: 0, g: 255, b: 0})
    })

    document.getElementById('console').value += '\n Colour changed to Green'
})


document.getElementById('blue').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/colour', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({r: 0, g: 0, b: 255})


    })
 
    document.getElementById('console').value += '\n Colour changed to Blue'
})



document.getElementById('roll').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/roll', {method: 'POST'})
    const data = await result.json()
    document.getElementById('console').value += '\n Rolling......'

})

document.getElementById('spin').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/spin', {method: 'POST'})
    const data = await result.json()
    document.getElementById('console').value += '\n Spinning...'
})

document.getElementById('stop').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/stop', {method: 'POST'})
    const data = await result.json()
    document.getElementById('console').value += '\n Stopped.'
})

