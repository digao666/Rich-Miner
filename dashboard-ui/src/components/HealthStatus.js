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
            // <div>
            //     <h1>Service Status</h1>
            //     <table className={"StatusTable"}>
            //         <tbody>
			// 		    <thead>
            //                 <th>Service</th>
            //                 <th>Status</th>
			// 			</thead>
			// 			<tr>
			// 				<td>Receiver:</td>
			// 				<td>{stats['receiver']}</td>
			// 			</tr>
			// 			<tr>
			// 				<td>storage:</td>
			// 				<td>{stats['storage']}</td>
			// 			</tr>
            //             <tr>
			// 				<td>Processing:</td>
			// 				<td>{stats['processing']}</td>
			// 			</tr>
            //             <tr>
			// 				<td>Audit_log:</td>
			// 				<td>{stats['audit_log']}</td>
			// 			</tr>
			// 		</tbody>
            //     </table>
            //     <h3>Last Updated: {stats['last_updated']}</h3>
            // </div>
            <div>
            <h1><span class="blue">&lt;</span>Table<span class="blue">&gt;</span> <span class="yellow">Responsive</pan></h1>
            <h2>Created with love by <a href="https://github.com/pablorgarcia" target="_blank">Pablo García</a></h2>
            
            <table class="container">
              <thead>
                <tr>
                  <th><h1>Sites</h1></th>
                  <th><h1>Views</h1></th>
                  <th><h1>Clicks</h1></th>
                  <th><h1>Average</h1></th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Google</td>
                  <td>9518</td>
                  <td>6369</td>
                  <td>01:32:50</td>
                </tr>
                <tr>
                  <td>Twitter</td>
                  <td>7326</td>
                  <td>10437</td>
                  <td>00:51:22</td>
                </tr>
                <tr>
                  <td>Amazon</td>
                  <td>4162</td>
                  <td>5327</td>
                  <td>00:24:34</td>
                </tr>
                <tr>
                  <td>LinkedIn</td>
                  <td>3654</td>
                  <td>2961</td>
                  <td>00:12:10</td>
                </tr>
                <tr>
                  <td>CodePen</td>
                  <td>2002</td>
                  <td>4135</td>
                  <td>00:46:19</td>
                </tr>
                <tr>
                  <td>GitHub</td>
                  <td>4623</td>
                  <td>3486</td>
                  <td>00:31:52</td>
                </tr>
              </tbody>
            </table>
            </div>
        )
    }
}
