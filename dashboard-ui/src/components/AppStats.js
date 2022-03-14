import React, { useEffect, useState} from 'react'
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
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
					  <thead>
                            <tr>
                                <th>Temperature</th>
                                <th>Value</th>
                            </tr>
						</thead>
						<tr>
							<td>Core Temperature count</td>
                            <td>{stats['num_core_temp']}</td>
						</tr>
						<tr>
							<td>Shell Temperature count</td>
                            <td>{stats['num_shell_temp']}</td>
						</tr>
						<tr>
							<td>Max Shell Temperature</td>
							<td>{stats['max_shell_temp']}</td>
						</tr>
						<tr>
							<td>Max Core Temperature</td>
							<td>{stats['max_core_temp']}</td>
						</tr>
					</tbody>
					<tbody>
					  <thead>
                            <tr>
                                <th>Fan Speed</th>
                                <th>Value</th>
                            </tr>
						</thead>
						<tr>
							<td>Fan Speed count</td>
							<td>{stats['num_fan_speed']}</td>
						</tr>
						<tr>
							<td>Max Fan Speed</td>
							<td>{stats['max_fan_speed']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
