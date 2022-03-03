import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://digao3855.westus3.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
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
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Temperature</th>
							<th>Fan Speed</th>
						</tr>
						<tr>
							<td># CORETEMP: {stats['num_core_temp']}</td>
                            <td># SHELLTEMP: {stats['num_shell_temp']}</td>
							<td># FS: {stats['num_fan_speed']}</td>
						</tr>
						<tr>
							<td colspan="2">Average Shell Temperature: {stats['avg_shell_temp']}</td>
						</tr>
						<tr>
							<td colspan="2">Average Core Temperature: {stats['avg_core_temp']}</td>
						</tr>
						<tr>
							<td colspan="2">Average Fan Speed: {stats['avg_fan_speed']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
