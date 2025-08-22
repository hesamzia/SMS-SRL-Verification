var trafficchart = document.getElementById("trafficflow");
var saleschart = document.getElementById("sales");

// new
var myChart3 = new Chart(trafficchart, {
type: 'pie',
data: {
    labels: ["Engineering", "Customer Support", "Operations", "Marketing", "R and D"],
    datasets: [{
        data: ["62", "80", "30", "25", "17"],
        backgroundColor: ["#009688", "#795548", "#673AB7", "#2196F3", "#6da252"],
        hoverOffset: 4
    }]
},
options: {
    animation: {
        duration: 2000,
        easing: 'easeOutQuart',
    },
    plugins: {
        legend: {
            display: true,
            position: 'right',
        },
        title: {
            display: false,
            text: 'Total Value',
            position: 'left',
        },
    },
}
});

// new
var myChart2 = new Chart(saleschart, {
type: 'bar',
data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [{
            label: 'Income',
            data: ["280", "300", "400", "600", "450", "400", "500", "550", "450", "650", "950", "1000"],
            backgroundColor: "rgba(76, 175, 80, 0.5)",
            borderColor: "#6da252",
            borderWidth: 1,
    }]
},
options: {
    animation: {
        duration: 2000,
        easing: 'easeOutQuart',
    },
    plugins: {
        legend: {
            display: false,
            position: 'top',
        },
        title: {
            display: true,
            text: 'Number of Sales',
            position: 'left',
        },
    },
}
});
