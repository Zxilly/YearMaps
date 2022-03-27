import React, {useEffect, useState} from 'react';
import './App.css';
import {Card, Image} from "antd";
import {API_URI, BASE_URI, TIME_URI} from "./Utils";


function App(): JSX.Element {
    const [pics, setPics] = useState<string[][]>([])
    const [update, setUpdate] = useState("")

    useEffect(() => {
        fetch(API_URI)
            .then(res => res.json())
            .then(data => {
                setPics(data)
            })
        fetch(TIME_URI)
            .then(res => res.json())
            .then(data => {
                setUpdate(data)
            })
    }, [])

    return (
        <main>
            {pics.map((provider: string[]) => {
                return (
                    <Card>
                        <Image preview={false} src={`${BASE_URI}/${provider[2]}`}/>
                    </Card>
                )
            })}
            <Card>
                <h3>
                    更新于 {update}
                </h3>
            </Card>
        </main>
    )
}

export default App;
