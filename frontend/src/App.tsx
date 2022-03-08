import React, {useEffect, useState} from 'react';
import './App.css';
import './Custom.css'
import {Card, Image} from "antd";
import {API_URI, BASE_URI} from "./Utils";


function App(): JSX.Element {
    const [pics, setPics] = useState<string[][]>([])

    useEffect(() => {
        fetch(API_URI)
            .then(res => res.json())
            .then(data => {
                setPics(data)
            })
    }, [])

    return (
        <main>
            {pics.map((provider: string[]) => {
                return (
                    <Card>
                        <Image src={`${BASE_URI}/${provider[2]}`}/>
                    </Card>
                )
            })}
        </main>
    )
}

export default App;
