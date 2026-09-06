const clock = document.getElementById("clock");
const year = document.getElementById("year");

function tick() {
  const now = new Date();
  const hangzhou = new Intl.DateTimeFormat("zh-CN", {
    timeZone: "Asia/Shanghai",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(now);

  if (clock) {
    clock.textContent = hangzhou;
    clock.dateTime = now.toISOString();
  }
}

tick();
setInterval(tick, 1000);

if (year) {
  year.textContent = String(new Date().getFullYear());
}
