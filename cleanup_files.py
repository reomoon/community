#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오래된 파일 정리 스크립트
일주일 이상된 output/crawl_results와 capture 폴더의 파일들을 자동 삭제
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class FileCleanupManager:
    def __init__(self):
        self.base_dir = Path(".")
        self.output_dir = self.base_dir / "output"
        self.capture_dir = self.base_dir / "capture"
        self.retention_days = 7  # 7일 보관
        
    def get_cutoff_date(self):
        """삭제 기준 날짜 계산 (7일 이전)"""
        return datetime.now() - timedelta(days=self.retention_days)
    
    def cleanup_output_files(self):
        """output 폴더의 오래된 crawl_results 파일들 삭제"""
        if not self.output_dir.exists():
            print("📁 output 폴더가 존재하지 않습니다.")
            return 0
        
        cutoff_date = self.get_cutoff_date()
        deleted_count = 0
        
        print(f"🗑️ output 폴더 정리 시작 (기준일: {cutoff_date.strftime('%Y-%m-%d')})")
        
        try:
            for file_path in self.output_dir.glob("crawl_results_*.json"):
                # 파일의 수정 시간 확인
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    try:
                        file_path.unlink()
                        print(f"  ✅ 삭제됨: {file_path.name} ({file_mtime.strftime('%Y-%m-%d %H:%M')})")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  ❌ 삭제 실패: {file_path.name} - {e}")
                else:
                    print(f"  ⏳ 보관: {file_path.name} ({file_mtime.strftime('%Y-%m-%d %H:%M')})")
            
            print(f"📊 output 폴더: {deleted_count}개 파일 삭제 완료")
            return deleted_count
            
        except Exception as e:
            print(f"❌ output 폴더 정리 중 오류: {e}")
            return 0
    
    def cleanup_capture_folders(self):
        """capture 폴더의 오래된 날짜 폴더들 삭제"""
        if not self.capture_dir.exists():
            print("📁 capture 폴더가 존재하지 않습니다.")
            return 0
        
        cutoff_date = self.get_cutoff_date()
        deleted_count = 0
        
        print(f"🗑️ capture 폴더 정리 시작 (기준일: {cutoff_date.strftime('%Y-%m-%d')})")
        
        try:
            for folder_path in self.capture_dir.iterdir():
                if folder_path.is_dir():
                    # 폴더명이 날짜 형식인지 확인 (YYYY-MM-DD)
                    try:
                        folder_date = datetime.strptime(folder_path.name, "%Y-%m-%d")
                        
                        if folder_date < cutoff_date:
                            try:
                                # 폴더 내 파일 개수 확인
                                file_count = len(list(folder_path.glob("*")))
                                shutil.rmtree(folder_path)
                                print(f"  ✅ 삭제됨: {folder_path.name}/ ({file_count}개 파일)")
                                deleted_count += 1
                            except Exception as e:
                                print(f"  ❌ 삭제 실패: {folder_path.name}/ - {e}")
                        else:
                            file_count = len(list(folder_path.glob("*")))
                            print(f"  ⏳ 보관: {folder_path.name}/ ({file_count}개 파일)")
                            
                    except ValueError:
                        # 날짜 형식이 아닌 폴더는 무시
                        print(f"  ⏭️ 건너뛰기: {folder_path.name}/ (날짜 형식 아님)")
            
            print(f"📊 capture 폴더: {deleted_count}개 폴더 삭제 완료")
            return deleted_count
            
        except Exception as e:
            print(f"❌ capture 폴더 정리 중 오류: {e}")
            return 0
    
    def get_storage_info(self):
        """저장소 사용량 정보 출력"""
        try:
            total_output_files = len(list(self.output_dir.glob("*.json"))) if self.output_dir.exists() else 0
            total_capture_folders = len([d for d in self.capture_dir.iterdir() if d.is_dir()]) if self.capture_dir.exists() else 0
            
            print(f"\n📋 현재 저장소 상태:")
            print(f"  📄 output 파일: {total_output_files}개")
            print(f"  📁 capture 폴더: {total_capture_folders}개")
            
        except Exception as e:
            print(f"⚠️ 저장소 정보 확인 실패: {e}")
    
    def run_cleanup(self):
        """전체 정리 작업 실행"""
        print(f"🧹 파일 정리 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 보관 기간: {self.retention_days}일 (이후 자동 삭제)")
        
        # 정리 전 현재 상태
        self.get_storage_info()
        
        # 파일 정리 실행
        output_deleted = self.cleanup_output_files()
        capture_deleted = self.cleanup_capture_folders()
        
        # 정리 후 상태
        self.get_storage_info()
        
        # 결과 요약
        print(f"\n✅ 정리 완료!")
        print(f"📊 총 삭제: output {output_deleted}개 파일, capture {capture_deleted}개 폴더")
        
        return output_deleted + capture_deleted

def main():
    """메인 실행 함수"""
    cleanup_manager = FileCleanupManager()
    deleted_total = cleanup_manager.run_cleanup()
    
    if deleted_total > 0:
        print(f"\n🎉 정리 작업이 성공적으로 완료되었습니다!")
    else:
        print(f"\n😊 삭제할 오래된 파일이 없습니다.")

if __name__ == "__main__":
    main()