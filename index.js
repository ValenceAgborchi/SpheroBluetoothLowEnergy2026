document.getElementById('connecttosphero').addEventListener('click', async () => {
    const result = await fetch('http://localhost:5000/connect', { method :'POST' })
    const data = await result.json()
    document.getElementById('console').value += '/n Connected!'

})

