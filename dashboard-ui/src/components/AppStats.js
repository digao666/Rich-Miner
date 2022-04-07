import React, { useEffect, useState} from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)
	const getStats = () => {
        fetch(`http://digao3855.westus3.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    };

    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
        <div>
            <h1><span class="yellow">Latest Stats</span></h1>
            <h2>Created with love by <a href="https://github.com/digao666/Rich-Miner.git" target="_blank">Di Gao</a></h2>
            <h2><span class="blue">Update every 5 seconds</span></h2>
            <table class="container">
                <thead>
                    <tr>
                        <th><h1>Service</h1></th>
                        <th><h1>Status</h1></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td>Core Temperature count:</td>
                    <td>{stats['num_core_temp']}</td>
                    </tr>
                    <tr>
                        <td>Shell Temperature count:</td>
                        <td>{stats['num_shell_temp']}</td>
                    </tr>
                    <tr>
                        <td>Max Shell Temperature:</td>
                        <td>{stats['max_shell_temp']}</td>
                    </tr>
                    <tr>
                        <td>Max Core Temperature:</td>
                        <td>{stats['max_core_temp']}</td>
                    </tr>
                </tbody>
                
                <thead>
                    <tr>
                        <th><h1>Service</h1></th>
                        <th><h1>Status</h1></th>
                    </tr>
                </thead>
                <tbody>

                    <tr>
                    <td>Fan Speed count:</td>
                    <td>{stats['num_fan_speed']}</td>
                    </tr>
                    <tr>
                        <td>Max Fan Speed:</td>
                        <td>{stats['max_fan_speed']}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        )
    }
}
