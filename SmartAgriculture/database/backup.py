"""
Database Backup and Recovery Utilities
Provides backup functionality for all databases in the hybrid storage system
"""
import os
import sys
import subprocess
import logging
import tarfile
import gzip
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Manages database backups for all database systems"""
    
    def __init__(self, backup_dir: str = "backups"):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Database configurations
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'agriculture'),
            'user': os.getenv('POSTGRES_USER', 'admin'),
            'password': os.getenv('POSTGRES_PASSWORD', 'admin123')
        }
        
        self.timescale_config = {
            'host': os.getenv('TIMESCALE_HOST', 'localhost'),
            'port': os.getenv('TIMESCALE_PORT', '5433'),
            'database': os.getenv('TIMESCALE_DB', 'agriculture_ts'),
            'user': os.getenv('POSTGRES_USER', 'admin'),
            'password': os.getenv('POSTGRES_PASSWORD', 'admin123')
        }
        
        self.mongo_config = {
            'host': os.getenv('MONGO_HOST', 'localhost'),
            'port': os.getenv('MONGO_PORT', '27017'),
            'database': os.getenv('MONGO_DB', 'agriculture')
        }
        
        self.neo4j_config = {
            'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            'user': os.getenv('NEO4J_USER', 'neo4j'),
            'password': os.getenv('NEO4J_PASSWORD', 'password')
        }
        
        # Backup metadata
        self.backup_metadata = {}
        
    def backup_postgres(self, output_file: Optional[str] = None) -> bool:
        """
        Backup PostgreSQL database
        
        Args:
            output_file: Optional output file path
            
        Returns:
            True if backup successful
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = self.backup_dir / f"postgres_{timestamp}.sql"
            
            # Use pg_dump
            cmd = [
                'pg_dump',
                '-h', self.postgres_config['host'],
                '-p', self.postgres_config['port'],
                '-U', self.postgres_config['user'],
                '-d', self.postgres_config['database'],
                '-f', str(output_file),
                '--verbose',
                '--no-password'
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.postgres_config['password']
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Compress the backup
                compressed_file = self._compress_file(output_file)
                
                # Record metadata
                self.backup_metadata['postgres'] = {
                    'timestamp': datetime.now().isoformat(),
                    'file': str(compressed_file),
                    'size_mb': compressed_file.stat().st_size / (1024 * 1024),
                    'database': self.postgres_config['database']
                }
                
                logger.info(f"✓ PostgreSQL backup completed: {compressed_file}")
                return True
            else:
                logger.error(f"✗ PostgreSQL backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ PostgreSQL backup error: {e}")
            return False
    
    def backup_timescale(self, output_file: Optional[str] = None) -> bool:
        """
        Backup TimescaleDB database
        
        Args:
            output_file: Optional output file path
            
        Returns:
            True if backup successful
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = self.backup_dir / f"timescale_{timestamp}.sql"
            
            # Use pg_dump (TimescaleDB is PostgreSQL-compatible)
            cmd = [
                'pg_dump',
                '-h', self.timescale_config['host'],
                '-p', self.timescale_config['port'],
                '-U', self.timescale_config['user'],
                '-d', self.timescale_config['database'],
                '-f', str(output_file),
                '--verbose',
                '--no-password'
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.timescale_config['password']
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Compress the backup
                compressed_file = self._compress_file(output_file)
                
                # Record metadata
                self.backup_metadata['timescale'] = {
                    'timestamp': datetime.now().isoformat(),
                    'file': str(compressed_file),
                    'size_mb': compressed_file.stat().st_size / (1024 * 1024),
                    'database': self.timescale_config['database']
                }
                
                logger.info(f"✓ TimescaleDB backup completed: {compressed_file}")
                return True
            else:
                logger.error(f"✗ TimescaleDB backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ TimescaleDB backup error: {e}")
            return False
    
    def backup_mongodb(self, output_file: Optional[str] = None) -> bool:
        """
        Backup MongoDB database
        
        Args:
            output_file: Optional output file path
            
        Returns:
            True if backup successful
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = self.backup_dir / f"mongodb_{timestamp}"
                output_dir.mkdir(exist_ok=True)
            else:
                output_dir = Path(output_file).with_suffix('')
                output_dir.mkdir(exist_ok=True)
            
            # Use mongodump
            cmd = [
                'mongodump',
                '--host', self.mongo_config['host'],
                '--port', self.mongo_config['port'],
                '--db', self.mongo_config['database'],
                '--out', str(output_dir),
                '--gzip'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Create tar archive
                compressed_file = self._compress_directory(output_dir)
                
                # Record metadata
                self.backup_metadata['mongodb'] = {
                    'timestamp': datetime.now().isoformat(),
                    'file': str(compressed_file),
                    'size_mb': compressed_file.stat().st_size / (1024 * 1024),
                    'database': self.mongo_config['database']
                }
                
                logger.info(f"✓ MongoDB backup completed: {compressed_file}")
                return True
            else:
                logger.error(f"✗ MongoDB backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"✗ MongoDB backup error: {e}")
            return False
    
    def backup_neo4j(self, output_file: Optional[str] = None) -> bool:
        """
        Backup Neo4j database
        
        Args:
            output_file: Optional output file path
            
        Returns:
            True if backup successful
        """
        try:
            if not output_file:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = self.backup_dir / f"neo4j_{timestamp}"
            else:
                output_dir = Path(output_file)
            
            output_dir.mkdir(exist_ok=True)
            
            # Use neo4j-admin dump command
            # Note: This requires Neo4j to be stopped or using online backup
            # For production, use neo4j-admin backup or Neo4j's backup service
            
            # Alternative: Export using Cypher queries
            from neo4j import GraphDatabase
            
            driver = GraphDatabase.driver(
                self.neo4j_config['uri'],
                auth=(self.neo4j_config['user'], self.neo4j_config['password'])
            )
            
            with driver.session() as session:
                # Export all nodes
                nodes_query = """
                MATCH (n)
                RETURN labels(n) AS labels, properties(n) AS props, id(n) AS id
                """
                nodes_result = session.run(nodes_query)
                nodes = [dict(record) for record in nodes_result]
                
                # Export all relationships
                rels_query = """
                MATCH (a)-[r]->(b)
                RETURN type(r) AS type, properties(r) AS props, 
                       id(a) AS start_id, id(b) AS end_id
                """
                rels_result = session.run(rels_query)
                relationships = [dict(record) for record in rels_result]
                
                # Save to JSON
                import json
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'database': 'neo4j',
                    'nodes': nodes,
                    'relationships': relationships
                }
                
                backup_file = output_dir / 'graph_backup.json'
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2, default=str)
            
            driver.close()
            
            # Compress
            compressed_file = self._compress_file(backup_file)
            
            # Record metadata
            self.backup_metadata['neo4j'] = {
                'timestamp': datetime.now().isoformat(),
                'file': str(compressed_file),
                'size_mb': compressed_file.stat().st_size / (1024 * 1024),
                'database': 'neo4j'
            }
            
            logger.info(f"✓ Neo4j backup completed: {compressed_file}")
            return True
                
        except Exception as e:
            logger.error(f"✗ Neo4j backup error: {e}")
            return False
    
    def backup_all(self) -> Dict[str, bool]:
        """
        Backup all databases
        
        Returns:
            Dictionary of backup results
        """
        logger.info("=" * 60)
        logger.info("STARTING FULL DATABASE BACKUP")
        logger.info("=" * 60)
        
        results = {}
        
        # Backup each database
        results['postgres'] = self.backup_postgres()
        results['timescale'] = self.backup_timescale()
        results['mongodb'] = self.backup_mongodb()
        results['neo4j'] = self.backup_neo4j()
        
        # Save metadata
        self._save_backup_metadata()
        
        logger.info("=" * 60)
        logger.info("BACKUP SUMMARY")
        logger.info("=" * 60)
        for db, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            logger.info(f"{db}: {status}")
        logger.info("=" * 60)
        
        return results
    
    def _compress_file(self, file_path: Path) -> Path:
        """
        Compress a file using gzip
        
        Args:
            file_path: Path to file to compress
            
        Returns:
            Path to compressed file
        """
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Remove original file
        file_path.unlink()
        
        return compressed_path
    
    def _compress_directory(self, dir_path: Path) -> Path:
        """
        Compress a directory into tar.gz
        
        Args:
            dir_path: Path to directory to compress
            
        Returns:
            Path to compressed file
        """
        compressed_path = dir_path.with_suffix('.tar.gz')
        
        with tarfile.open(compressed_path, 'w:gz') as tar:
            tar.add(dir_path, arcname=dir_path.name)
        
        # Remove original directory
        import shutil
        shutil.rmtree(dir_path)
        
        return compressed_path
    
    def _save_backup_metadata(self):
        """Save backup metadata to JSON file"""
        try:
            metadata_file = self.backup_dir / 'backup_metadata.json'
            
            metadata = {
                'backup_date': datetime.now().isoformat(),
                'backups': self.backup_metadata
            }
            
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"✓ Backup metadata saved: {metadata_file}")
            
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")
    
    def get_backup_list(self) -> list:
        """
        Get list of available backups
        
        Returns:
            List of backup files
        """
        backups = []
        
        for file in self.backup_dir.glob('*.gz'):
            backups.append({
                'file': file.name,
                'path': str(file),
                'size_mb': file.stat().st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(file.stat().st_ctime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, days: int = 30) -> int:
        """
        Remove backups older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of backups deleted
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted_count = 0
            
            for file in self.backup_dir.glob('*.gz'):
                if file.stat().st_ctime < cutoff_date:
                    file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {file.name}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0


def backup_all_databases(backup_dir: str = "backups") -> Dict[str, bool]:
    """
    Convenience function to backup all databases
    
    Args:
        backup_dir: Directory to store backups
        
    Returns:
        Dictionary of backup results
    """
    manager = DatabaseBackup(backup_dir)
    return manager.backup_all()


def backup_postgres_only(backup_dir: str = "backups") -> bool:
    """
    Convenience function to backup only PostgreSQL
    
    Args:
        backup_dir: Directory to store backups
        
    Returns:
        True if backup successful
    """
    manager = DatabaseBackup(backup_dir)
    return manager.backup_postgres()


def backup_timescale_only(backup_dir: str = "backups") -> bool:
    """
    Convenience function to backup only TimescaleDB
    
    Args:
        backup_dir: Directory to store backups
        
    Returns:
        True if backup successful
    """
    manager = DatabaseBackup(backup_dir)
    return manager.backup_timescale()


def backup_mongodb_only(backup_dir: str = "backups") -> bool:
    """
    Convenience function to backup only MongoDB
    
    Args:
        backup_dir: Directory to store backups
        
    Returns:
        True if backup successful
    """
    manager = DatabaseBackup(backup_dir)
    return manager.backup_mongodb()


def backup_neo4j_only(backup_dir: str = "backups") -> bool:
    """
    Convenience function to backup only Neo4j
    
    Args:
        backup_dir: Directory to store backups
        
    Returns:
        True if backup successful
    """
    manager = DatabaseBackup(backup_dir)
    return manager.backup_neo4j()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Backup Utility')
    parser.add_argument('--all', action='store_true', help='Backup all databases')
    parser.add_argument('--postgres', action='store_true', help='Backup PostgreSQL only')
    parser.add_argument('--timescale', action='store_true', help='Backup TimescaleDB only')
    parser.add_argument('--mongodb', action='store_true', help='Backup MongoDB only')
    parser.add_argument('--neo4j', action='store_true', help='Backup Neo4j only')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--cleanup', type=int, help='Delete backups older than N days')
    parser.add_argument('--dir', default='backups', help='Backup directory')
    
    args = parser.parse_args()
    
    if args.list:
        manager = DatabaseBackup(args.dir)
        backups = manager.get_backup_list()
        
        if backups:
            print("\nAvailable Backups:")
            print("=" * 80)
            for backup in backups:
                print(f"File: {backup['file']}")
                print(f"  Size: {backup['size_mb']:.2f} MB")
                print(f"  Created: {backup['created']}")
                print()
        else:
            print("No backups found")
    
    elif args.cleanup:
        manager = DatabaseBackup(args.dir)
        deleted = manager.cleanup_old_backups(args.cleanup)
        print(f"Deleted {deleted} old backups")
    
    elif args.all:
        backup_all_databases(args.dir)
    
    elif args.postgres:
        backup_postgres_only(args.dir)
    
    elif args.timescale:
        backup_timescale_only(args.dir)
    
    elif args.mongodb:
        backup_mongodb_only(args.dir)
    
    elif args.neo4j:
        backup_neo4j_only(args.dir)
    
    else:
        parser.print_help()