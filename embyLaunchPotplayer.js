// ==UserScript==
// @name         embyLaunchPotplayer
// @name:en      embyLaunchPotplayer
// @name:zh      embyLaunchPotplayer
// @name:zh-CN   embyLaunchPotplayer
// @namespace    http://tampermonkey.net/
// @version      0.9
// @description  try to take over the world!
// @description:zh-cn emby调用外部播放器
// @include       *m35134*
// @include       *:8*
// ==/UserScript==

//修改此处api_key为你自己的
const api_key = "7753ae02845a4e968eeb39aca46c03e3";

const reg = /\/[a-z]{2,}\/\S*?id=/;

let timer = setInterval(function() {
    let potplayer = document.querySelectorAll("div[is='emby-scroller']:not(.hide) .potplayer")[0];
    if(!potplayer){
        let mainDetailButtons = document.querySelectorAll("div[is='emby-scroller']:not(.hide) .mainDetailButtons")[0];
        if(mainDetailButtons){
            let buttonhtml = `<div class ="flex">
                  <button id="embyPot" type="button" class="detailButton  emby-button potplayer" title="Potplayer"> <div class="detailButton-content"> <i class="md-icon detailButton-icon"></i>  <div class="detailButton-text">PotPlayer</div> </div> </button>
                 </div>`
            mainDetailButtons.insertAdjacentHTML('afterend', buttonhtml)
            document.querySelector("div[is='emby-scroller']:not(.hide) #embyPot").onclick = embyPot;
        }
    }
}, 1000)

async function getItemInfo(){
    let itemInfoUrl = window.location.href.replace(reg, "/emby/Items/").split('&')[0] + "/PlaybackInfo?api_key=" + api_key;
    console.log("itemInfo：" + itemInfoUrl);
    let response = await fetch(itemInfoUrl);
    if(response.ok)
    {
        return await response.json();
    }else{
        alert("获取视频信息失败,检查api_key是否设置正确  "+response.status+" "+response.statusText);
        throw new Error(response.statusText);
    }
}

function getSeek(){
    let resumeButton = document.querySelector("div[is='emby-scroller']:not(.hide) div.resumeButtonText");
    let seek = '';
    if (resumeButton) {
        if (resumeButton.innerText.includes('恢复播放')) {
            seek = resumeButton.innerText.replace('恢复播放', '').replace('从', '').replace(' ', '');
        }
    }
    return seek;
}

function getHDR(){
    let result = document.evaluate('/html/body/div[5]/div/div/div[1]/div[2]/div[2]/div[2]/form/div[2]/select/option[1]', document).iterateNext()
    let hdr = '';
    if (result.innerText.includes('HDR')) {
        hdr = 'hdr';
    }
    return hdr;
}

function getSubUrl(itemInfo, MediaSourceIndex){
    let selectSubtitles = document.querySelector("div[is='emby-scroller']:not(.hide) select.selectSubtitles");
    let subTitleUrl = '';
    if (selectSubtitles) {
        if (selectSubtitles.value > 0) {
            if (itemInfo.MediaSources[MediaSourceIndex].MediaStreams[selectSubtitles.value].IsExternal) {
                let subtitleCodec = itemInfo.MediaSources[MediaSourceIndex].MediaStreams[selectSubtitles.value].Codec;
                let MediaSourceId = itemInfo.MediaSources[MediaSourceIndex].Id;
                let domain = window.location.href.replace(reg, "/emby/videos/").split('&')[0];
                subTitleUrl = `${domain}/${MediaSourceId}/Subtitles/${selectSubtitles.value}/${MediaSourceIndex}/Stream.${subtitleCodec}?api_key=${api_key}`;
                console.log(subTitleUrl);
            }
        }
    }
    return subTitleUrl;
}


async function getEmbyMediaUrl() {
    let selectSource = document.querySelector("div[is='emby-scroller']:not(.hide) select.selectSource");
    //let selectAudio = document.querySelector("div[is='emby-scroller']:not(.hide) select.selectAudio");
    let itemInfo = await getItemInfo();
    let MediaSourceIndex = 0;
    for(let i = 0; i< itemInfo.MediaSources.length; i++){
        if(itemInfo.MediaSources[i].Id == selectSource.value){
            MediaSourceIndex = i;
        };
    }
    let container = itemInfo.MediaSources[MediaSourceIndex].Container;
    let MediaSourceId = selectSource.value;
    let PlaySessionId = itemInfo.PlaySessionId;
    let subUrl = await getSubUrl(itemInfo, MediaSourceIndex);
    let domain = window.location.href.replace(reg, "/emby/videos/").split('&')[0];
    console.log(domain)
    let streamUrl = `${domain}/stream.${container}?api_key=${api_key}&Static=true&MediaSourceId=${MediaSourceId}&PlaySessionId=${PlaySessionId}`;
    console.log(streamUrl,subUrl)
    return Array(streamUrl, subUrl);
}

async function embyPot() {
    let mediaUrl = await getEmbyMediaUrl();
    let poturl = `emby://${encodeURI(mediaUrl[0])} /sub=${encodeURI(mediaUrl[1])} /current /seek=${getSeek()} ${getHDR()}`;
    console.log(poturl);
    console.log(getHDR());
    window.open(poturl, "_blank");
}
