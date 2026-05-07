// Configuration: set your intervals and corresponding postfix
const timeConfig = [
  { start: 0, end: 4, postfix: "natt" },
  { start: 5, end: 8, postfix: "morgen" },
  { start: 9, end: 18, postfix: "dag" },
  { start: 19, end: 23, postfix: "aften" }
];

function getCurrentPostfix() {
  const hour = new Date().getHours();
  for (const interval of timeConfig) {
    if (hour >= interval.start && hour <= interval.end) {
      return interval.postfix;
    }
  }
  return "day"; // fallback
}

function setHeaderImage() {
  const imgElement = document.getElementById("header-img");
  const baseName = imgElement.dataset.base || "header";
  const fileExt = imgElement.dataset.ext || ".gif";

  const postfix = getCurrentPostfix();
  imgElement.src = `${baseName}${postfix}${fileExt}`;
}

function scheduleNextUpdate() {
  const now = new Date();
  const msUntilNextHour =
    (60 - now.getMinutes()) * 60 * 1000 -
    now.getSeconds() * 1000 -
    now.getMilliseconds();

  setTimeout(() => {
    setHeaderImage();
    scheduleNextUpdate();
  }, msUntilNextHour);
}

// Run once the page is loaded
document.addEventListener("DOMContentLoaded", () => {
  setHeaderImage();
  scheduleNextUpdate();
});
