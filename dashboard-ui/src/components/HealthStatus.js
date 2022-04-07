import React, { useEffect, useState} from 'react'
import '../App.css';

export default function HealthStatus() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)
	const getHealth = () => {
        fetch(`http://digao3855.westus3.cloudapp.azure.com/health/status`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    };

    useEffect(() => {
		const interval = setInterval(() => getHealth(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getHealth]);
    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
            <h1><span class="yellow">Service Status</span></h1>
            <h2>Created with love by <a href="https://github.com/digao666/Rich-Miner.git" target="_blank">Di Gao</a></h2>
            <h2><span class="blue">Update every 20 seconds</span></h2>
            <table class="container">
                <thead>
                    <tr>
                        <th><h1>Service</h1></th>
                        <th><h1>Status</h1></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Receiver:</td>
                        <td>{stats['receiver']}</td>
                    </tr>
                    <tr>
                        <td>storage:</td>
                        <td>{stats['storage']}</td>
                    </tr>
                    <tr>
                        <td>Processing:</td>
                        <td>{stats['processing']}</td>
                    </tr>
                    <tr>
                        <td>Audit_log:</td>
                        <td>{stats['audit_log']}</td>
                    </tr>
                </tbody>
            </table>
            </div>
        )
    }
}
