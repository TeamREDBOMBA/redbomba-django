moment.locale('ko', {
    months: "1월_2월_3월_4월_5월_6월_7월_8월_9월_10월_11월_12월".split("_"),
    monthsShort: "1월_2월_3월_4월_5월_6월_7월_8월_9월_10월_11월_12월".split("_"),
    weekdays: "일요일_월요일_화요일_수요일_목요일_금요일_토요일".split("_"),
    weekdaysShort: "일_월_화_수_목_금_토".split("_"),
    weekdaysMin: "일_월_화_수_목_금_토".split("_"),
    longDateFormat: {
        LT: "A h시 mm분",
        LTS: "A h시 mm분 ss초",
        L: "YYYY-MM-DD",
        LL: "YYYY년 MMMM D일",
        LLL: "YYYY년 MMMM D일 A h시 mm분",
        LLLL: "YYYY년 MMMM D일 dddd A h시 mm분"
    },
    relativeTime: {
        future: "%s 후",
        past: "%s 전",
        s: "방금",
        m: "1분",
        mm: "%d분",
        h: "1시간",
        hh: "%d시간",
        d: "1일",
        dd: "%d일",
        M: "1달",
        MM: "%d 달",
        y: "1년",
        yy: "%d년"
    },
    meridiem: {
        am: "오전",
        AM: "오전",
        pm: "오후",
        PM: "오후"
    },
    calendar: {
        lastDay: "[어제] LT",
        sameDay: "[오늘] LT",
        nextDay: "[내일] LT",
        lastWeek: "[지난 주] dddd LT",
        nextWeek: "dddd LT",
        sameElse: "LL"
    },
    ordinal : function (number, token) {
        return "일";
    }
});
